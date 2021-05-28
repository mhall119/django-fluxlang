from django_fluxlang import Flux

def print_results(query):
    for table in query:
        for row in table.records:
            print(f'{row.values["_time"]}: ', end='')
            for key in row.values:
                print(f'{key}={row.values[key]} ', end='')
            print()
    print('success')

cpu = Flux.bucket('website').range(start='-5m', stop='-0s').filter(_measurement='cpu', _field='usage_user')
print("CPU query")
print("-------------------")
print(cpu)
print("-------------------")
print_results(cpu)
print("\n")

mean_cpu = cpu.aggregateWindow(every='1m', fn='mean').filter(host='gettogether.community')
print("Mean CPU query")
print("-------------------")
print(mean_cpu)
print("-------------------")
print_results(mean_cpu)
print("\n")


disk = Flux.bucket('website').range(start='-5m', stop='-0s').filter(_measurement='disk', _field='used')
print("Disk query")
print("-------------------")
print(disk)
print("-------------------")
print_results(disk)
print("\n")

joined = Flux.join(tables=[cpu, disk], on=['_time', 'host'])
print("Joined query")
print("-------------------")
print(joined)
print("-------------------")
print_results(joined)
print("\n")

localhost = joined.filter(host='gettogether.community').fieldsAsCols()
print("Filtered Join Query")
print("-------------------")
print(localhost)
print("-------------------")
print_results(localhost)
print("\n")

