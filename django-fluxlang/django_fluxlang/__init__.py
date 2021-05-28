from influxdb_client import InfluxDBClient
from django.db.models import QuerySet
from django.conf import settings

class FluxQuery():
    
    def __init__(self, previous_query=None, flux=None):
        self.query_steps = []
        if previous_query is not None:
            self.query_steps += previous_query.query_steps
            self.script = previous_query.script
        else:
            self.script = Flux()

        if flux is not None:
            self.query_steps.append(flux)

    def range(self, start, stop=None):
        if stop is not None:
            return FluxQuery(self, "  |> range(start:%s, stop:%s)" % (start, stop))
        else:
            return FluxQuery(self, "  |> range(start:%s)" % start)

    def filter(self, **kwargs):
        new_query = FluxQuery(self)
        for key, value in kwargs.items():
            new_query.query_steps.append("  |> filter(fn: (r) => r[\"%s\"] == \"%s\")" % (key, value))
        return new_query

    def aggregateWindow(self, every, fn, createEmpty=False):
        return FluxQuery(self, "  |> aggregateWindow(every: %s, fn: %s, createEmpty: %s)" % (every, fn, str(createEmpty).lower()))

    def fieldsAsCols(self):
        self.script.imports.add("influxdata/influxdb/v1")
        return FluxQuery(self, "  |> v1.fieldsAsCols()")

    def __str__(self):
        return "\n".join(self.query_steps)

    def flux(self):
        full_query = []
        for flux_import in self.script.imports:
            full_query.append("import \"%s\"" % flux_import)
        full_query.append("\n")
        for step in self.query_steps:
            full_query.append(step)
        return "\n".join(full_query)

    def __iter__(self):
        influxdb = settings.DATABASES['influxdb']
        client = InfluxDBClient(url=influxdb['URL'], org=influxdb['ORG'], token=influxdb['TOKEN'])
        query_api = client.query_api()
        tables = query_api.query(query=self.flux())
        for table in tables:
            yield table

class JoinedFluxQuery(FluxQuery):

    def __init__(self, queries, keys):
        super().__init__()

        self.script = Flux()
        self.keys = ",".join(["\"%s\"" % key for key in keys])
        self.named_queries = []
        for i, query in enumerate(queries):
            query_name="query_%s" % i
            if isinstance(query, FluxQuery):
                self.script.imports.update(query.script.imports)
                self.query_steps.append("%s = %s" % (query_name, str(query)))
            elif isinstance(query, QuerySet):
                self.query_steps.append("%s = %s" % (query_name, self.sql_from(query)))
            self.named_queries.append(query_name)
        self.query_steps.append("\njoin(tables:{%s}, on:[%s])" % (','.join(self.named_queries), self.keys))

    def sql_from(self, queryset):
        self.script.imports.add("sql")
        dbinfo = settings.DATABASES[queryset.db]
        return """sql.from(
  driverName: "%(driver)s",
  dataSourceName: "%(connect_string)s",
  query:"%(query)s"
)""" % {
    'driver': dbinfo['ENGINE'].split(".")[-1],
    'connect_string': "file:%s?cache=shared&mode=ro" % dbinfo['NAME'],
    'query': str(queryset.query).replace("\"", "\\\""),
}

class Flux():

    def __init__(self):
        self.named_query_count = 0
        self.imports = set()

    @classmethod
    def bucket(cls, bucket):
        return FluxQuery(flux="from(bucket:\"%s\")" % bucket)

    @classmethod
    def join(cls, tables, on):
        return JoinedFluxQuery(queries=tables, keys=on)