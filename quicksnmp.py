from pysnmp import hlapi
import sys


def get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types(oids)
    )
    return fetch(handler, 1)[0]


def construct_object_types(list_of_oids):
    object_types = []
    for oid in list_of_oids:
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
    return object_types


def fetch(handler, count):
    result = []
    for i in range(count):
        try:
            error_indication, error_status, error_index, var_binds = next(
                handler)
            if not error_indication and not error_status:
                items = {}
                for var_bind in var_binds:
                    items[str(var_bind[0])] = cast(var_bind[1])
                result.append(items)
            else:
                raise RuntimeError(
                    'Got SNMP error: {0}'.format(error_indication))
        except StopIteration:
            break
    return result


def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value


def get_bulk(target, oids, credentials, count, start_from=0, port=161,
             engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.bulkCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        start_from, count,
        *construct_object_types(oids)
    )
    return fetch(handler, count)


def get_bulk_auto(target, oids, credentials, count_oid, start_from=0, port=161,
                  engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    count = get(target, [count_oid], credentials,
                port, engine, context)[count_oid]
    return get_bulk(target, oids, credentials, count, start_from, port, engine, context)


def runNetstat(host, protocol):

    tcp = get_bulk(host, ['1.3.6.1.2.1.6.13.1.1'], hlapi.UsmUserData(
        'usuariosnmp', authKey='udescudesc', privKey='udescudesc'), 100)

    udp = get_bulk(host, ['1.3.6.1.2.1.7.5.1.1'], hlapi.UsmUserData(
        'usuariosnmp', authKey='udescudesc', privKey='udescudesc'), 100)

    # itsT = get_bulk_auto('127.0.0.1', ['1.3.6.1.2.1.6.13.1.1'], hlapi.UsmUserData(
    #   'usuariosnmp', authKey='udescudesc', privKey='udescudesc'), '1.3.6.1.2.1.2.1.0')

    #    itsU = get_bulk_auto('127.0.0.1', ['1.3.6.1.2.1.7.5.1.1'], hlapi.UsmUserData(
    #       'usuariosnmp', authKey='udescudesc', privKey='udescudesc'), '1.3.6.1.2.1.7.2.0')

    if(protocol == '-TCP' or protocol == 'UDP/TCP'):
        print("################## TCP ################")
        count = 0
        for it in tcp:

            for k, v in it.items():
                if (v == 5):
                    print(count, ")", sep='')
                    count += 1
                    aux = k.split('.')

                    print("LocalAddress: ", aux[10], ".", aux[11], ".",
                          aux[12], ".", aux[13], " LocalPort: ", aux[14], sep='')
                    print("RemAddress: ", aux[15], ".", aux[16], ".",
                          aux[17], ".", aux[18], " RemPort: ", aux[19], sep='')
                    print("status: STABLISHED (5)")
                    print('')

    if(protocol == '-UDP' or protocol == 'UDP/TCP'):
        print("################## UDP ################")

        count = 0

        for it in udp:
            print(count, ")", sep='')
            count += 1
            for k, v in it.items():
                aux = k.split('.')

                print(aux[-5], ".", aux[-4], ".", aux[-3],
                      ".", aux[-2], ":", aux[-1], sep='')
            print('')


host = '127.0.0.1'
protocol = 'UDP/TCP'

if len(sys.argv) == 2:
    if str(sys.argv[1]) in ['-TCP', '-UDP']:
        protocol = str(sys.argv[1])
    else:
        host = str(sys.argv[1])
elif len(sys.argv) == 3:
    host = str(sys.argv[1])
    protocol = str(sys.argv[2])


print("host:", host, "protocol:", protocol)
print("Starting NETSTAT...")

runNetstat(host, protocol)
