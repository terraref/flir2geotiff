'''
Created on Aug 23, 2016

@author: Zongyang Li
'''

import sys, math
import numpy as np
from numpy.matlib import repmat


class calibParam:
    def __init__(self):
        self.calibrated = True
        self.calibrationR = 0.0
        self.calibrationB = 0.0
        self.calibrationF = 0.0
        self.calibrationJ1 = 0.0
        self.calibrationJ0 = 0.0
        self.calibrationa1 = 0.0
        self.calibrationa2 = 0.0
        self.calibrationX = 0.0
        self.calibrationb1 = 0.0
        self.calibrationb2 = 0.0


def rawData_to_temperature(rawData, metadata):
    try:
        calibP = get_calibrate_param(metadata)
        tc = np.zeros((640, 480))
        
        if calibP.calibrated:
            tc = rawData/10
        else:
            tc = flirRawToTemperature(rawData, calibP)

        return tc
    except Exception as ex:
        fail('raw to temperature fail:' + str(ex))


def get_calibrate_param(metadata):
    calibparameter = calibParam()

    try:
        if 'terraref_cleaned_metadata' in metadata:
            fixedmd = metadata['sensor_fixed_metadata']
            if fixedmd['is_calibrated'] == 'True':
                return calibparameter
            else:
                calibparameter.calibrated = False
                calibparameter.calibrationR = float(fixedmd['calibration_R'])
                calibparameter.calibrationB = float(fixedmd['calibration_B'])
                calibparameter.calibrationF = float(fixedmd['calibration_F'])
                calibparameter.calibrationJ1 = float(fixedmd['calibration_J1'])
                calibparameter.calibrationJ0 = float(fixedmd['calibration_J0'])
                calibparameter.calibrationa1 = float(fixedmd['calibration_alpha1'])
                calibparameter.calibrationa2 = float(fixedmd['calibration_alpha2'])
                calibparameter.calibrationX = float(fixedmd['calibration_X'])
                calibparameter.calibrationb1 = float(fixedmd['calibration_beta1'])
                calibparameter.calibrationb2 = float(fixedmd['calibration_beta2'])
                return calibparameter

    except KeyError as err:
        return calibparameter


# convert flir raw data into temperature C degree, for date after September 15th
def flirRawToTemperature(rawData, calibP):
    
    R = calibP.calibrationR
    B = calibP.calibrationB
    F = calibP.calibrationF
    J0 = calibP.calibrationJ0
    J1 = calibP.calibrationJ1
    
    X = calibP.calibrationX
    a1 = calibP.calibrationa1
    b1 = calibP.calibrationb1
    a2 = calibP.calibrationa2
    b2 = calibP.calibrationb2
    
    H2O_K1 = 1.56
    H2O_K2 = 0.0694
    H2O_K3 = -0.000278
    H2O_K4 = 0.000000685
    
    H = 0.1
    T = 22.0
    D = 2.5
    E = 0.98
    
    K0 = 273.15
    
    im = rawData
        
    AmbTemp = T + K0
    AtmTemp = T + K0
        
    H2OInGperM2 = H*math.exp(H2O_K1 + H2O_K2*T + H2O_K3*math.pow(T, 2) + H2O_K4*math.pow(T, 3))
    a1b1sqH2O = (a1+b1*math.sqrt(H2OInGperM2))
    a2b2sqH2O = (a2+b2*math.sqrt(H2OInGperM2))
    exp1 = math.exp(-math.sqrt(D/2)*a1b1sqH2O)
    exp2 = math.exp(-math.sqrt(D/2)*a2b2sqH2O)
        
    tao = X*exp1 + (1-X)*exp2
        
    obj_rad = im*E*tao
        
    theo_atm_rad = (R*J1/(math.exp(B/AtmTemp)-F)) + J0
    atm_rad = repmat((1-tao)*theo_atm_rad, 640, 480)
        
    theo_amb_refl_rad = (R*J1/(math.exp(B/AmbTemp)-F)) + J0
    amb_refl_rad = repmat((1-E)*tao*theo_amb_refl_rad, 640, 480)
        
    corr_pxl_val = obj_rad + atm_rad + amb_refl_rad
        
    pxl_temp = B/np.log(R/(corr_pxl_val-J0)*J1+F)
    
    return pxl_temp


def fail(reason):
    print >> sys.stderr, reason
