import os
import sqlite3
import contextlib

from yax.state.type import Int, Str, Float, File, Directory


@contextlib.contextmanager
def auto_rollback(conn):
    """Create a contextual cursor which automatically rollbacks/commit changes.

    On an exception, the cursor will be rolled back. Otherwise the cursor's
    changes are committed to the database and the cursor is closed.

    Parameters
    ----------
    conn : sqlite3.connection
        A connection to a sqlite3 database

    Yields
    ------
        A safe sqlite3.cursor with automatic rollback and commits

    """
    cursor = conn.cursor()
    try:
        yield cursor
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        cursor.close()


class ArtifactMap:
    def __init__(self, artifact_dir, db_fp, exe_graph):
        """Initialize an ArtifactMap

        If the database has not yet been created, the `exe_graph` will be
        traversed to generate a schema.

        Parameters
        ----------
        artifact_dir : path to directory
            The root directory in which to store artifacts
        db_fp : filepath
            Where to place the database
        exe_graph : ExeGraph
            An instance of the pipeline

        """
        # sqlite3.connect will create a database if it doesn't already exist,
        # so cache existence before connection
        db_exists = os.path.isfile(db_fp)

        self.graph = exe_graph
        self.conn = sqlite3.connect(db_fp)
        self.artifact_dir = artifact_dir

        if not db_exists:
            self._init_database()

    def get_arguments_for_node(self, node, run_id):
        """Get the input arguments for a given node from the database.

        Paramters
        ---------
        node : ExeNode
            The node to get corresponding arguments for.
        run_id : int
            The run ID for which the arguments are associated.

        Returns
        -------
        dict
            Maps node input arguments names to their values for a `run_id`

        Raises
        ------
        LookupError
            Raised when the `run_id` does not exist in the database.

        """
        input_params = node.get_input_params().keys()
        params_names = ["_".join([node.name, key]) for key in input_params]
        sql = """
            SELECT %s FROM Run WHERE id = ?
        """ % ','.join(params_names)
        with auto_rollback(self.conn) as c:
            c.execute(sql, (run_id,))
            values = c.fetchone()
        if values is None:
            raise LookupError("Provided `run_id` (%r) does not exist."
                              % run_id)
        return dict(zip(input_params, values))

    def declare_artifacts(self, config, run_id):
        """Declare artifacts which are not yet associated with `run_id`.

        If an artifact has already been created with arguments matching its
        position in the pipeline, associate it with this `run_id`. Otherwise,
        create a new artifact and associate it with this `run_id`.

        Parameters
        ----------
        config : dict of dicts
            Maps section name to dict of parameters and their arguments.
        run_id : int
            The run ID to associate the new (or existing) artifacts with.

        Returns
        -------
        None

        """
        for bound_artifact, nodes in \
                self.graph.bound_artifact_to_upstream_nodes.items():
            # Only the params which impact the creation of the artifact need
            # to be checked for.
            relevant_params = self._flatten_config(
                {node.name: config[node.name] for node in nodes})

            rows = self._find_existing_artifacts(bound_artifact,
                                                 relevant_params)
            if len(rows) == 0:
                self._declare_new_artifact(bound_artifact, run_id)
            else:
                for a_id, r_id in rows:
                    if r_id == run_id:
                        # We've encountered ourselves, something strange must
                        # have happened during a previous prep
                        continue
                    self._insert_into(
                        'Artifact_Run',
                        {'run_id': run_id, 'artifact_id': a_id})

    def _declare_new_artifact(self, bound_artifact, run_id):
        """Create a fresh artifact, creating the directory and entries."""
        path = os.path.join(self.artifact_dir,
                            "_".join([str(run_id), bound_artifact, 'art']))
        os.mkdir(path)
        artifact_id = self._insert_into("Artifact", {'name': bound_artifact,
                                                     'path': path})
        if not artifact_id:
            raise Exception("This shouldn't have happened. Ask Mike what went "
                            "wrong. mikedeberg@gmail.com")

        self._insert_into("Artifact_Run",
                          {'run_id': run_id, 'artifact_id': artifact_id})

    def declare_run(self, config):
        """Create or find a run for the given config.

        Parameters
        ----------
        config : dict of dicts
            Maps section name to dict of parameters and their arguments.

        Returns
        -------
        (int, str)
            The first element is a run ID, created or otherwise. The second is
            an existing run key if am identical run exists, otherwise an empty
            string.

        Raises
        ------
        ValueError
            Raised when a config contains a run key which is already in the
            database with differing arguments.

        """
        config = self._flatten_config(config)
        run_id = self._insert_into("Run", config)
        run_key = ""
        if not run_id:
            # The insert failed, this could be for 2 reasons:
            # - UNIQUE constraint on run_key failed
            # - UNIQUE constraint on all parameters failed
            debug_run_key = config.pop("run_key")
            row = self._select_all_from('Run', config)
            if not row:
                # It wasn't the constraint on all parameters
                raise ValueError("This run key %r already exists."
                                 % debug_run_key)
            else:
                # Identical run has already happened, use it instead
                row, = row
                run_id = row[0]
                run_key = row[1]

        return run_id, run_key

    def run_key_to_run_id(self, run_key):
        """Convert a `run_key` to a run ID.

        Parameters
        ----------
        run_key : str
            A run key to search for.

        Returns
        -------
        int
            The run ID

        Raises
        ------
        LookupError
            Raised if the `run_key` does not exist.

        """

        rows = self._select_all_from('Run', {'run_key': run_key})
        if not rows:
            raise LookupError("Run key %r does not exist or has not"
                              " been prepared." % run_key)
        return rows[0][0]

    def bound_artifact_to_filepath(self, run_id):
        """Maps bound artifact names to the filepaths associated with `run_id`.

        Parameters
        ----------
        run_id : int
            Artifact filepaths returned will be associated with this `run_id`.

        Returns
        -------
        dict
            Maps bound artifact names to their filepaths

        Raises
        ------
        LookupError
            Raised when `run_id` does not exist or does not have any artifacts.

        """
        sql = '''
            SELECT A.name, A.path FROM
                Artifact AS A
            INNER JOIN
                Artifact_Run AS AR ON A.id = AR.artifact_id
            WHERE
                AR.run_id = ?
        '''
        with auto_rollback(self.conn) as c:
            c.execute(sql, (run_id,))
            rows = c.fetchall()

        if not rows:
            raise LookupError("`run_id` (%r) does not exist or does not have"
                              " any artifacts")
        return dict(rows)

    def get_details(self, run_id):
        """Gets the pipeline details from the database for a given `run_id`.

        Parameters
        ----------
        run_id : int
            The run ID for which to get the associated pipeline details.

        Returns
        -------
        dict
            Maps pipeline details parameters to their arguments for a `run_id`.

        Raises
        ------
        LookupError
            Raised if a `run_id` does not exist.

        """
        details = sorted([x if x == 'run_key' else 'details_' + x
                          for x in self.graph.details])
        sql = """
            SELECT %s FROM Run WHERE id = ?
        """ % ','.join(details)
        with auto_rollback(self.conn) as c:
            c.execute(sql, (run_id,))
            result = c.fetchone()

        if result is None:
            raise LookupError("`run_id` (%r) does not exist." % run_id)

        details_ = []
        for detail in details:
            if detail.startswith("details_"):
                detail = detail.split("_", 1)[1]
            details_.append(detail)

        return dict(zip(details_, result))

    def _flatten_config(self, config):
        """Flatten a dict of dicts into a dict namespaced by the outer key."""
        results = {}
        for section_key, section in config.items():
            for key, value in section.items():
                results["%s_%s" % (section_key, key)] = value
        if 'details_run_key' in results:
            results['run_key'] = results.pop("details_run_key")
        return results

    def _insert_into(self, table, values):
        """Insert values into a table, ignoring constraint failures (no op).

        Parameters
        ----------
        table : str
            The name of the table to insert into.
        values : dict
            Mapping of column names to arguments to insert as a new row.

        """
        with auto_rollback(self.conn) as c:
            # SQL Injection is possible, but honestly, all you would accomplish
            # is screwing up a directory. We still use '?' because it would be
            # nice if SQLite told us something was wrong.
            c.execute("INSERT OR IGNORE INTO %s (%s) VALUES (%s)"
                      % (table, ','.join(values),
                         ','.join(['?'] * len(values))),
                      tuple(values.values()))

            return c.lastrowid

    def _select_all_from(self, table, where):
        where_sql = " AND ".join(["%s=?" % key for key in where.keys()])
        with auto_rollback(self.conn) as c:
            c.execute("SELECT * FROM %s WHERE %s"
                      % (table, where_sql), tuple(where.values()))
            return c.fetchall()

    def _find_existing_artifacts(self, artifact_name, params):
        sql = """
            SELECT A.id, R.id FROM
                (SELECT * FROM Run WHERE %s) AS R
            INNER JOIN
                Artifact_Run AS AR ON R.id = AR.run_id
            INNER JOIN
                Artifact AS A ON A.id = AR.artifact_id
            WHERE
                A.name = ?
        """ % " AND ".join(["%s=?" % key for key in params.keys()])

        with auto_rollback(self.conn) as c:
            args = tuple(list(params.values()) + [artifact_name])
            c.execute(sql, args)
            return c.fetchall()

    # The following are all database inititalization helpers.

    def _init_database(self):
        with auto_rollback(self.conn) as c:
            c.execute('CREATE TABLE Run (\n    %s\n)' % self._make_run_cols([
                ('id', 'INTEGER', 'PRIMARY KEY', 'NOT NULL'),
                ('run_key', 'TEXT', 'UNIQUE', 'NOT NULL'),
            ]))

            c.execute('''
            CREATE TABLE Artifact_Run (
                artifact_id    INTEGER    NOT NULL,
                run_id         INTEGER    NOT NULL,
                FOREIGN KEY(artifact_id) REFERENCES Artifact(id),
                FOREIGN KEY(run_id) REFERENCES Run(id)
            )
            ''')

            c.execute('''
            CREATE TABLE Artifact (
                id      INTEGER     PRIMARY KEY    NOT NULL,
                name    TEXT                       NOT NULL,
                path    TEXT                       NOT NULL
            )
            ''')

    def _make_run_cols(self, columns):
        for key, value in self.graph.details.items():
            type_ = value
            if type(value) is tuple:
                type_, _ = value
            field_name = "details_%s" % key
            field_type = self._translate_param_to_type(type_)
            if field_name != 'details_run_key':
                columns.append((field_name, field_type, '', 'NOT NULL'))

        for node in self.graph:
            for param, param_type in node.get_input_params().items():
                field_name = "%s_%s" % (node.name, param)
                field_type = self._translate_param_to_type(param_type)
                columns.append((field_name, field_type, '', "NOT NULL"))
        return ",\n    ".join(self._pretty_format_columns(columns) +
                              ["UNIQUE(%s)" % ", ".join(
                                [x[0] for x in columns[2:]])])

    def _translate_param_to_type(self, param_type):
        return {
            Int: 'INTEGER',
            Str: 'TEXT',
            Float: 'REAL',
            File: 'TEXT',
            Directory: 'TEXT'
        }[param_type]

    def _pretty_format_columns(self, columns):
        new_cols = []
        for def_cols in zip(*columns):
            max_len = max(map(len, def_cols))
            new_cols.append([c + (" " * (max_len - len(c))) for c in def_cols])
        return ['    '.join(column).rstrip() for column in zip(*new_cols)]
