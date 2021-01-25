#!/usr/bin/python3
import numpy as np
import math



def f32(m3, idx):
    v = m3[idx:idx+4].view(dtype=np.dtype(np.float32))
#   print(v)
    return float(v[0])

def u16(m3, idx):
    v = m3[idx:idx+4].view(dtype=np.dtype(np.uint16))
#   print(v)
    return int(v[0])

Fix_, Distance_, refltmp_, airtmp_, Humi_, Emiss_ = 0., 0., 0., 0., 0., 0.
fpatmp_, fpaavg_, orgavg_, coretmp_ = 0., 0., 0., 0.

part_emi_t_1, part_Tatm_Trefl = 0., 0.
flt_10003360, flt_1000335C, flt_1000339C, flt_100033A4, flt_10003398 = 0., 0., 0., 0., 0.
flt_10003394 = 0., 0., 0.

ABSOLUTE_ZERO_CELSIUS = -273.15



def sub_10001180(coretmp_, cx):
    global Distance_, refltmp_, airtmp_, Humi_, Emiss_

    # based on:
    # https://www.mdpi.com/1424-8220/17/8/1718 page: 4
    # https://github.com/mcguire-steve/ht301_ircam

    # w - coefficient showing the content of water vapour in atmosphere
    h0 = 1.5587
    h1 = 0.06938999999999999
    h2 = -0.00027816
    h3 = 0.00000068455

    w = math.exp(h3 * airtmp_ ** 3 + h2  * airtmp_ ** 2 + h1 * airtmp_ + h0) * Humi_

    # K_atm - scaling factor for the atmosphere damping
    # a1,a2 - attenuation for atmosphere without water vapor
    # b1,b2 - attenuation for water vapor
    
    K_atm = 1.9
    a1, a2 = 0.0066, 0.0126
    b1, b2 = -0.0023, -0.0067

    #t - transmittance of the atmosphere 
    d_ = -Distance_**0.5
    w_ = w ** 0.5
    t =  K_atm * math.exp(d_ * (a1 + b1 * w_)) + (1. - K_atm) * math.exp(d_ * (a2 + b2 * w_))
    print('water vapour content coefficient:', w)
    print('transmittance of atmosphere:     ', t)

    part_emi_t_1 = 1.0 / (Emiss_ * t)
    part_Tatm_Trefl = (1.0 - Emiss_) * t * (refltmp_ - ABSOLUTE_ZERO_CELSIUS)**4  +  (1.0 - t) * (airtmp_ - ABSOLUTE_ZERO_CELSIUS)**4

#---------------------
    # a1 = coretmp_
    # flt_100033A4 = fpatmp_ 

    l_flt_1000337C = flt_1000335C / (2.0 * flt_10003360)
    l_flt_1000337C_2 = l_flt_1000337C **2


    v23 = flt_10003360 * coretmp_**2 + flt_1000335C * coretmp_;
    v22 = flt_1000339C * fpatmp_**2 + flt_10003398 * fpatmp_ + flt_10003394;

    type_ = 0
    if type_ != 0:
        v2 = 0;
    else:
        v2 = int(390.0 - fpatmp_ * 7.05)
    v4 = cx - v2;
    v5 = -v4;
    p = [];
    if (Distance_ >= 20):
        distance_c = (20        * 0.85 - 1.125) / 100.
    else:
        distance_c = (Distance_ * 0.85 - 1.125) / 100.
    for i in range(16384):
        v8 = float(v5 * v22 + v23) / flt_10003360 + l_flt_1000337C_2
        Ttot = float(v8)**0.5 - l_flt_1000337C - ABSOLUTE_ZERO_CELSIUS
        Tobj_C = ((Ttot**4 - part_Tatm_Trefl) * part_emi_t_1)**0.25 + ABSOLUTE_ZERO_CELSIUS
        p.append(Tobj_C + distance_c * (Tobj_C - airtmp_))
        v5 += 1

    #print('p:',p)
    return p


#fpa <- focal-plane array (sensor)

def temperatureLut(meta0, meta3):

    global Fix_, Distance_, refltmp_, airtmp_, Humi_, Emiss_
    global fpatmp_, fpaavg_, orgavg_, coretmp_ 

    global part_emi_t_1, part_Tatm_Trefl
    global flt_10003360, flt_1000335C, flt_1000339C, flt_100033A4, flt_10003398
    global flt_10003394

    m3 = meta3.view(dtype=np.dtype(np.uint8))

    v5 = meta3[0];
    coretmp_ = float(meta3[1]) / 10.0 + ABSOLUTE_ZERO_CELSIUS;
    fpatmp_ = 20.0 - (float(meta0[1]) - 7800) / 36.0;

    flt_10003360 = f32(m3, 6);
    flt_1000335C = f32(m3, 10);
    flt_1000339C = f32(m3, 14);
    flt_10003398 = f32(m3, 18);
    flt_10003394 = f32(m3, 22);
    readParaFromDevFlag = True
    if readParaFromDevFlag:
        print('m3:', m3[127*2:127*2+30])
        Fix_ = f32(m3,127*2);
        refltmp_ = f32(m3,127*2 + 4);
        airtmp_ = f32(m3,127*2 + 8);
        Humi_ = f32(m3,127*2 + 12);
        Emiss_ = f32(m3,127*2 + 16);
        Distance_ = u16(m3,127*2 + 20);
        #readParaFromDevFlag = 0;

    print('Fix_',Fix_)
    print('refltmp_',refltmp_)
    print('airtmp_',airtmp_)
    print('Humi_',Humi_)
    print('Emiss_',Emiss_)
    print('Distance_',Distance_)

    print()
    print('v5',v5)
    print('coretmp_',coretmp_, meta3[1])
    print('fpatmp_',fpatmp_, meta0[1])
    print()
    print('flt_10003360',flt_10003360)
    print('flt_1000335C',flt_1000335C)
    print('flt_1000339C',flt_1000339C)
    print('flt_10003398',flt_10003398)
    print('flt_10003394',flt_10003394)

    return sub_10001180(coretmp_, v5); #//bug in IDA


def info(frame):

    print('shape:',frame.shape)
    Height_, Width_ = 288, 384
    meta = frame[Height_:, ...]
    meta = meta.reshape(4,384)
    meta0, meta3 = meta[0], meta[3]

    temperatureLUT = temperatureLut(meta0, meta3)

#    print('meta0 :',meta0.tolist())
#    print('meta12:',meta[1:2].tolist())
#    print('meta3 :',meta3.tolist())
#    print(float(meta0[1]))
    fpatmp_ = 20.0 - (float(meta0[1]) - 7800.0) / 36.0;
    print('fpatmp_:', fpatmp_)
    fpaavg_ = meta0[0]
    orgavg_ = meta0[8];
    coretmp_ = float(meta3[1]) / 10.0 - 273.1;

    Fix_ = 0.
    centertmp = temperatureLUT[meta0[12]] + Fix_;
    maxtmp = temperatureLUT[meta0[4]] + Fix_;
    mintmp = temperatureLUT[meta0[7]] + Fix_;
    maxx = meta0[2];
    maxy = meta0[3];
    minx = meta0[5];
    miny = meta0[6];

    print('m:',maxx, maxy, minx, miny)
    print('orgavg_:',orgavg_, 'coretmp_:', coretmp_)
    print('fpaavg_:',fpaavg_)
    print('centtemp_raw:', meta0[12])
    print('max_tmp_raw:', meta0[4])
    print('min_tmp_raw:', meta0[7])

    print('arr0_tmp_raw:', meta0[13])
    print('arr1_tmp_raw:', meta0[14])
    print('arr2_tmp_raw:', meta0[15])

    print('mintmp:', mintmp, 'maxtmp', maxtmp)
    print('centertmp:',centertmp)
    centertmp

    print('')
    #tmparr = temperatureLUT[v13[13]] + Fix_;
    #tmparr[1] = temperatureLUT[v13[14]] + Fix_;
    #tmparr[2] = temperatureLUT[v13[15]] + Fix_;

    
