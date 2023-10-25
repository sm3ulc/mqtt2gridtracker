

def isloc(loc):
    if len(loc) != 4 or loc == 'RR73':
        return False
    if loc[0].isalpha() and loc[1].isalpha() and loc[2].isdigit() and loc[3].isdigit():
        return True
    return False


def decode21(data):


    data = data[12:]
    strl = int.from_bytes(data[0:4], byteorder='big')
    app_id = data[4:4+strl].decode("utf-8")
    print("app-id", app_id)
    data = data[4+strl:]

    # Dial freq
    dial_freq = int.from_bytes(data[0:8], byteorder='big')
    print("dial", dial_freq, data[0:8])
    data = data[8:]


    # Mode
    strl = int.from_bytes(data[0:4], byteorder='big')
    mode = data[4:4+strl].decode("utf-8")
    data = data[4+strl:]
    print("mode:", strl, mode)
    
    
    # DX call
    strl = int.from_bytes(data[0:4], byteorder='big')
    if strl == 4294967295:
        strl = 0

    dx_call = data[4:4+strl].decode("utf-8")
    data = data[4+strl:]

    print("DX", dx_call, strl)

    # Report
    strl = int.from_bytes(data[0:4], byteorder='big')
    report = data[4:4+strl].decode("utf-8")
    data = data[4+strl:]

    print("report", report, strl)

    # Tx-mode
    strl = int.from_bytes(data[0:4], byteorder='big')
    txmode = data[4:4+strl].decode("utf-8")
    data = data[4+strl:]

    print("txmode", txmode, strl)

    # Status
    txenabled = int(data[0])
    transmitting = int(data[1])
    decoding = int(data[2])
    data = data[3:]

    # TX & RX drift
    rx_df = int.from_bytes(data[0:4], byteorder='big')
    tx_df = int.from_bytes(data[4:8], byteorder='big')
    data = data[8:]


    # DE call
    strl = int.from_bytes(data[0:4], byteorder='big')
    if strl == 4294967295:
        strl = 0

    de_call = data[4:4+strl].decode("utf-8")
    data = data[4+strl:]

    # DE grid
    strl = int.from_bytes(data[0:4], byteorder='big')
    if strl == 4294967295:
        strl = 0

    de_grid = data[4:4+strl].decode("utf-8")
    data = data[4+strl:]

    print("de_grid", de_grid, strl, data)

    # DX grid
    strl = int.from_bytes(data[0:4], byteorder='big')
    if strl == 4294967295:
        strl = 0

    dx_grid = data[4:4+strl].decode("utf-8")
    print("dx-grid", dx_grid)
    data = data[4+strl:]


    # print("dog", data)

    # # Tx Watchdog
    # tx_watchdog = int(data[0])
    # data = data[1:]

    # print("subm", data)
        
    # # Sub-Mode
    # strl = int.from_bytes(data[0:4], byteorder='big')
    # submode = data[4:4+strl].decode("utf-8")
    # data = data[4+strl:]


    # print("fast", data)
    
    # # Fast mode
    # fast_mode = int(data[0])
    # data = data[1:]

    # # Special operation mode
    # spec_mode = int.from_bytes(data[0:0], byteorder='big')
    # data = data[1:]

    # 0 -> NONE
    # 1 -> NA VHF
    # 2 -> EU VHF
    # 3 -> FIELD DAY
    # 4 -> RTTY RU
    # 5 -> FOX
    # 6 -> HOUND

    # print(data)

    
    # Tx Watchdog            bool
    # Sub-mode               utf8
    # Fast mode              bool
    # Special operation mode quint8

    statusstrnew  =  "Dial: %s Mode: %s DXcall: %s Report: %s TXmode: %s TXe: %s TX: %s Dec %s rxdf %s txdf %s DEcall: %s  DEgrid: %s DXgrid: %s" % (dial_freq, mode, dx_call, report, txmode, txenabled, transmitting, decoding, rx_df, tx_df, de_call, de_grid, dx_grid)
    print(statusstrnew)

    #    print("DEcall", de_call, "DEgrid:", de_grid, "DXgrid:", dx_grid)

    #DEcall: %s  DEgrid: %s DXgrid: %s
    #    print(
    # print("watchdog:",  tx_watchdog, "fastmode", fast_mode, "special mode", spec_mode)
    # sys.exit(0)





def decode22(data):
    if debug:
        print("decode ")

    data = data[12:]
    strl = int.from_bytes(data[0:4], byteorder='big')
    app_id = data[4:4+strl].decode("utf-8")
    print("app-id", app_id)
    data = data[4+strl:]

    
    new = int(data[0])
    print("new", new)
    
    year = datetime.datetime.today().year
    month = datetime.datetime.today().month
    day = datetime.datetime.today().day
    qtime = int.from_bytes(data[1:5], byteorder='big')
    hour = int(qtime / (60 * 60 * 1000))
    minute = int((qtime  - (hour * 60 * 60 * 1000)) / (60 * 1000))
    second = int((qtime % (60 * 1000)) / 1000)
    time = datetime.datetime(year, month, day, hour, minute, second)
    print(time)

    snr = int.from_bytes(data[5:9], byteorder='big', signed=True)
    data = data[9:]
    print("snr", snr)
    
    #for c in data:
    #    print(hex(c)[2:], end=',')
    #print()
          
    delta_time = round(struct.unpack('>d',data[0:8])[0], 5)
    data = data[8:]

    print("deltatime:", delta_time)
    
    delta_fq = int.from_bytes(data[0:4], byteorder='big')
    data = data[4:]

    strl = int.from_bytes(data[0:4], byteorder='big')
    mode = data[4:4+strl].decode("utf-8")
    data = data[4+strl:]
    print("mode", mode)

    strl = int.from_bytes(data[0:4], byteorder='big')
    message = data[4:4+strl].decode("utf-8")
    data = data[4+strl:]
    print("message", message)

    low_conf = int(data[0])
    off_air = int(data[1])
    

    print("New: %s Time %s snr %4s dtime: %4s dfq: %4s mode: %s mess: %s" % (new, time, snr, delta_time, delta_fq, mode, message))

    mess_lst = message.split()
    if len(mess_lst) == 3 and mess_lst[0] == 'CQ' and isloc(mess_lst[2]):
        # elif len(mess_lst) == 3 and isloc(mess_lst[2])
        loc=message.split()[2]
        # print("CQ3", loc, maidenhead.toLoc(loc), len(callpos))
                   
    elif len(mess_lst) == 4 and mess_lst[0] == 'CQ' and isloc(mess_lst[3]):
        loc=message.split()[3]
        # print("CQ4", loc, maidenhead.toLoc(loc))


    elif len(mess_lst) == 3 and isloc(mess_lst[2]):
        loc=message.split()[2]

        # print(loc, maidenhead.toLoc(loc), len(callpos))
