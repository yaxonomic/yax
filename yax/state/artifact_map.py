import os
import sqlite3
import contextlib

from yax.state.type import Int, Str, Float, File, Directory


@contextlib.contextmanager
def auto_rollback(conn):
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
        db_exists = os.path.isfile(db_fp)

        self.graph = exe_graph
        self.conn = sqlite3.connect(db_fp)
        self.artifact_dir = artifact_dir

        if not db_exists:
            self._init_database()

    def get_params(self, run_id, node):
        input_params = node.get_input_params().keys()
        params_names = ["_".join([node.name, key]) for key in input_params]
        self._select_all_from('Run', {'id': run_id})

        sql = """
            SELECT %s FROM Run WHERE id = ?
        """ % ','.join(params_names)
        with auto_rollback(self.conn) as c:
            c.execute(sql, (run_id,))
            return dict(zip(input_params, c.fetchone()))

    def declare_artifacts(self, config, run_id):
        for bound_artifact, nodes in self.graph.artifact_dependencies.items():
            params = self._flatten_config({node.name: config[node.name]
                                           for node in nodes})
            rows = self._find_existing_artifacts(bound_artifact, params)
            if len(rows) == 0:
                self._declare_new_artifact(run_id, bound_artifact)
            else:
                for aid, rid in rows:
                    if rid == run_id:
                        continue
                    self._insert_into(
                        'Artifact_Run',
                        {'run_id': run_id, 'artifact_id': aid})

    def _declare_new_artifact(self, run_id, bound_artifact):
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

    def create_run(self, config):
        config = self._flatten_config(config)
        run_id = self._insert_into("Run", config)
        run_key = ""
        if not run_id:
            config.pop("run_key")
            row = self._select_all_from('Run', config)
            if not row:
                raise Exception("This run_key already exists.")
            else:
                row, = row

            run_id = row[0]
            run_key = row[1]

        return run_id, run_key

    def resolve_run_key(self, run_key):
        rows = self._select_all_from('Run', {'run_key': run_key})
        if not rows:
            raise ValueError("Run key %r does not exist or has not"
                             " been prepared." % run_key)
        return rows[0][0]

    def get_artifact_paths(self, run_id):
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
            return dict(c.fetchall())

    def get_details(self, run_id):
        details = sorted([x if x == 'run_key' else 'details_' + x
                          for x in self.graph.details])
        sql = """
            SELECT %s FROM Run WHERE id = ?
        """ % ','.join(details)
        with auto_rollback(self.conn) as c:
            c.execute(sql, (run_id,))

            details_ = []
            for detail in details:
                if detail.startswith("details_"):
                    detail = detail[len("details_"):]
                details_.append(detail)

            return dict(zip(details_, c.fetchone()))

    def _flatten_config(self, config):
        results = {}
        for section_key, section in config.items():
            for key, value in section.items():
                results["%s_%s" % (section_key, key)] = value
        if "details_run_key" in results:
            results['run_key'] = results.pop("details_run_key")
        return results

    def _insert_into(self, table, values):
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
