import os.path
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
    def __init__(self, db_fp, exe_graph):
        db_exists = os.path.isfile(db_fp)

        self.graph = exe_graph
        self.conn = sqlite3.connect(db_fp)

        if not db_exists:
            self._init_database()

    def get_artifact(self, artifact_name, params):
        pass

    def declare_artifact(self, artifact_name, artifact_fp):
        pass

    def _init_database(self):
        with auto_rollback(self.conn) as c:
            c.execute('CREATE TABLE Run (\n    %s\n)' % self._make_run_cols([
                ('id', 'INTEGER', 'PRIMARY KEY', 'NOT NULL'),
                ('name', 'TEXT', '', 'NOT NULL')
            ]))

            c.execute('''
            CREATE TABLE Artifact_Run (
                artifact_id    INTEGER    NOT NULL,
                run_id         INTEGER    NOT NULL
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
        for node in self.graph:
            for param, param_type in node.get_input_params().items():
                field_name = "%s_%s" % (node.name, param)
                field_type = self._translate_param_to_type(param_type)
                columns.append((field_name, field_type, '', "NOT NULL"))
        return ",\n    ".join(self._pretty_format_columns(columns))

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
