import pymodbus
import json
import sys, os, requests, datetime, re, logging, logging.handlers
import paho.mqtt.publish as publish
import pytz
import configparser
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pprint import pprint
from time import sleep


# Sleep time.
LOOP_SLEEP = 600
# Debug mode.
DEBUG = 0

class KsemMqtt():
    def init(self, logger, statuslogger):
        self.ksem_hostname = os.environ.get('ksem_hostname','')
        self.ksem_port = int(os.environ.get('ksem_port',''))
        
        self.mqtt_client_id = os.environ.get('mqtt_client_id','')
        self.mqtt_host = os.environ.get('mqtt_client_host','')
        self.mqtt_port = int(os.environ.get('mqtt_client_port',''))
        self.mqtt_topic = os.environ.get('mqtt_client_root_topic','')
        self.mqtt_qos = int(os.environ.get('mqtt_qos',''))
        self.mqtt_retain = eval(os.environ.get('mqtt_retain',''))
        
        if eval(os.environ.get('mqtt_auth','')):
            self.mqtt_username = os.environ.get('mqtt_username','')
            self.mqtt_password = os.environ.get('mqtt_password','')

        if eval(os.environ.get('mqtt_auth','')):
            self.mqtt_auth = { "username": os.environ.get('mqtt_username',''), "password": os.environ.get('mqtt_password','') }
        else:
            self.mqtt_auth = None

        self.logger = logger
        self.statuslogger = statuslogger
        
        #No more changes required beyond this point
        self.KostalRegister = []
        self.Adr0=[]
        self.Adr0=[0]
        self.Adr0.append("ActivePowerPlus")
        self.Adr0.append("U32")
        self.Adr0.append(0)
        
        self.Adr2=[]
        self.Adr2=[2]
        self.Adr2.append("ActivePowerMinus")
        self.Adr2.append("U32")
        self.Adr2.append(0)     
        
        self.Adr4=[]
        self.Adr4=[4]
        self.Adr4.append("ReactivePowerPlus")
        self.Adr4.append("U32")
        self.Adr4.append(0)
        
        self.Adr6=[]
        self.Adr6=[6]
        self.Adr6.append("ReactivePowerMinus")
        self.Adr6.append("U32")
        self.Adr6.append(0)     
        
        self.Adr16=[]
        self.Adr16=[16]
        self.Adr16.append("ApparentPowerPlus")
        self.Adr16.append("U32")
        self.Adr16.append(0)
        
        self.Adr18=[]
        self.Adr18=[18]
        self.Adr18.append("ApparentPowerMinus")
        self.Adr18.append("U32")
        self.Adr18.append(0)
        
        self.Adr24=[]
        self.Adr24=[24]
        self.Adr24.append("PowerFactor")
        self.Adr24.append("I32")
        self.Adr24.append(0)            

        self.Adr26=[]
        self.Adr26=[26]
        self.Adr26.append("SupplyFrequency")
        self.Adr26.append("U32")
        self.Adr26.append(0)    

        self.Adr40=[]
        self.Adr40=[40]
        self.Adr40.append("ActivePowerPlus_L1")
        self.Adr40.append("U32")
        self.Adr40.append(0)    

        self.Adr42=[]
        self.Adr42=[42]
        self.Adr42.append("ActivePowerMinus_L1")
        self.Adr42.append("U32")
        self.Adr42.append(0)    

        self.Adr44=[]
        self.Adr44=[44]
        self.Adr44.append("ReactivePowerPlus_L1")
        self.Adr44.append("U32")
        self.Adr44.append(0)
        
        self.Adr46=[]
        self.Adr46=[46]
        self.Adr46.append("ReactivePowerMinus_L1")
        self.Adr46.append("U32")
        self.Adr46.append(0)    

        self.Adr56=[]
        self.Adr56=[56]
        self.Adr56.append("ApparentPowerPlus_L1")
        self.Adr56.append("U32")
        self.Adr56.append(0)    

        self.Adr58=[]
        self.Adr58=[58]
        self.Adr58.append("ApparentPowerMinus_L1")
        self.Adr58.append("U32")
        self.Adr58.append(0)
        
        self.Adr60=[]
        self.Adr60=[60]
        self.Adr60.append("Current_L1")
        self.Adr60.append("U32")
        self.Adr60.append(0)    

        self.Adr62=[]
        self.Adr62=[62]
        self.Adr62.append("Voltage_L1")
        self.Adr62.append("U32")
        self.Adr62.append(0)    

        self.Adr64=[]
        self.Adr64=[64]
        self.Adr64.append("PowerFactor_L1")
        self.Adr64.append("I32")
        self.Adr64.append(0)    

        self.Adr80=[]
        self.Adr80=[80]
        self.Adr80.append("ActivePowerPlus_L2")
        self.Adr80.append("U32")
        self.Adr80.append(0)
        
        self.Adr82=[]
        self.Adr82=[82]
        self.Adr82.append("ActivePowerMinus_L2")
        self.Adr82.append("U32")
        self.Adr82.append(0)    

        self.Adr84=[]
        self.Adr84=[84]
        self.Adr84.append("ReactivePowerPlus_L2")
        self.Adr84.append("U32")
        self.Adr84.append(0)    

        self.Adr86=[]
        self.Adr86=[86]
        self.Adr86.append("ReactivePowerMinus_L2")
        self.Adr86.append("U32")
        self.Adr86.append(0)    

        self.Adr96=[]
        self.Adr96=[96]
        self.Adr96.append("ApparentPowerPlus_L2")
        self.Adr96.append("U32")
        self.Adr96.append(0)
        
        self.Adr98=[]
        self.Adr98=[98]
        self.Adr98.append("ApparentPowerMinus_L2")
        self.Adr98.append("U32")
        self.Adr98.append(0)    

        self.Adr100=[]
        self.Adr100=[100]
        self.Adr100.append("Current_L2")
        self.Adr100.append("U32")
        self.Adr100.append(0)   

        self.Adr102=[]
        self.Adr102=[102]
        self.Adr102.append("Voltage_L2")
        self.Adr102.append("U32")
        self.Adr102.append(0)   

        self.Adr104=[]
        self.Adr104=[104]
        self.Adr104.append("PowerFactor_L2")
        self.Adr104.append("I32")
        self.Adr104.append(0)
        
        self.Adr120=[]
        self.Adr120=[120]
        self.Adr120.append("ActivePowerPlus_L3")
        self.Adr120.append("U32")
        self.Adr120.append(0)   

        self.Adr122=[]
        self.Adr122=[122]
        self.Adr122.append("ActivePowerMinus_L3")
        self.Adr122.append("U32")
        self.Adr122.append(0)   

        self.Adr124=[]
        self.Adr124=[124]
        self.Adr124.append("ReactivePowerPlus_L3")
        self.Adr124.append("U32")
        self.Adr124.append(0)   

        self.Adr126=[]
        self.Adr126=[126]
        self.Adr126.append("ReactivePowerMinus_L3")
        self.Adr126.append("U32")
        self.Adr126.append(0)
        
        self.Adr136=[]
        self.Adr136=[136]
        self.Adr136.append("ApparentPowerPlus_L3")
        self.Adr136.append("U32")
        self.Adr136.append(0)   

        self.Adr138=[]
        self.Adr138=[138]
        self.Adr138.append("ApparentPowerMinus_L3")
        self.Adr138.append("U32")
        self.Adr138.append(0)   

        self.Adr140=[]
        self.Adr140=[140]
        self.Adr140.append("Current_L3")
        self.Adr140.append("U32")
        self.Adr140.append(0)   

        self.Adr142=[]
        self.Adr142=[142]
        self.Adr142.append("Voltage_L3")
        self.Adr142.append("U32")
        self.Adr142.append(0)

        self.Adr144=[]
        self.Adr144=[144]
        self.Adr144.append("PowerFactor_L3")
        self.Adr144.append("I32")
        self.Adr144.append(0)

        self.Adr512=[]
        self.Adr512=[512]
        self.Adr512.append("ActiveEnergyPlus")
        self.Adr512.append("UInt64")
        self.Adr512.append(0)   
        
        self.Adr516=[]
        self.Adr516=[516]
        self.Adr516.append("ActiveEnergyMinus")
        self.Adr516.append("UInt64")
        self.Adr516.append(0)   

        self.Adr520=[]
        self.Adr520=[520]
        self.Adr520.append("ReactiveEnergyPlus")
        self.Adr520.append("UInt64")
        self.Adr520.append(0)   

        self.Adr524=[]
        self.Adr524=[524]
        self.Adr524.append("ReactiveEnergyMinus")
        self.Adr524.append("UInt64")
        self.Adr524.append(0)           

        self.Adr544=[]
        self.Adr544=[544]
        self.Adr544.append("ApparentEnergyPlus")
        self.Adr544.append("UInt64")
        self.Adr544.append(0)   

        self.Adr548=[]
        self.Adr548=[548]
        self.Adr548.append("ApparentEnergyMinus")
        self.Adr548.append("UInt64")
        self.Adr548.append(0)   

        self.Adr592=[]
        self.Adr592=[592]
        self.Adr592.append("ActiveEnergyPlus_L1")
        self.Adr592.append("UInt64")
        self.Adr592.append(0)

        self.Adr596=[]
        self.Adr596=[596]
        self.Adr596.append("ActiveEnergyMinus_L1")
        self.Adr596.append("UInt64")
        self.Adr596.append(0)

        self.Adr600=[]
        self.Adr600=[600]
        self.Adr600.append("ReactiveEnergyPlus_L1")
        self.Adr600.append("UInt64")
        self.Adr600.append(0)

        self.Adr604=[]
        self.Adr604=[604]
        self.Adr604.append("ReactiveEnergyMinus_L1")
        self.Adr604.append("UInt64")
        self.Adr604.append(0)

        self.Adr624=[]
        self.Adr624=[624]
        self.Adr624.append("ApparentEnergyPlus_L1")
        self.Adr624.append("UInt64")
        self.Adr624.append(0)

        self.Adr628=[]
        self.Adr628=[628]
        self.Adr628.append("ApparentEnergyMinus_L1")
        self.Adr628.append("UInt64")
        self.Adr628.append(0)

        self.Adr672=[]
        self.Adr672=[672]
        self.Adr672.append("ActiveEnergyPlus_L2")
        self.Adr672.append("UInt64")
        self.Adr672.append(0)

        self.Adr676=[]
        self.Adr676=[676]
        self.Adr676.append("ActiveEnergyMinus_L2")
        self.Adr676.append("UInt64")
        self.Adr676.append(0)

        self.Adr680=[]
        self.Adr680=[680]
        self.Adr680.append("ReactiveEnergyPlus_L2")
        self.Adr680.append("UInt64")
        self.Adr680.append(0)

        self.Adr684=[]
        self.Adr684=[684]
        self.Adr684.append("ReactiveEnergyMinus_L2")
        self.Adr684.append("UInt64")
        self.Adr684.append(0)

        self.Adr704=[]
        self.Adr704=[704]
        self.Adr704.append("ApparentEnergyPlus_L2")
        self.Adr704.append("UInt64")
        self.Adr704.append(0)

        self.Adr708=[]
        self.Adr708=[708]
        self.Adr708.append("ApparentEnergyMinus_L2")
        self.Adr708.append("UInt64")
        self.Adr708.append(0)

        self.Adr752=[]
        self.Adr752=[752]
        self.Adr752.append("ActiveEnergyPlus_L3")
        self.Adr752.append("UInt64")
        self.Adr752.append(0)

        self.Adr756=[]
        self.Adr756=[756]
        self.Adr756.append("ActiveEnergyMinus_L3")
        self.Adr756.append("UInt64")
        self.Adr756.append(0)

        self.Adr760=[]
        self.Adr760=[760]
        self.Adr760.append("ReactiveEnergyPlus_L3")
        self.Adr760.append("UInt64")
        self.Adr760.append(0)

        self.Adr764=[]
        self.Adr764=[764]
        self.Adr764.append("ReactiveEnergyMinus_L3")
        self.Adr764.append("UInt64")
        self.Adr764.append(0)

        self.Adr784=[]
        self.Adr784=[784]
        self.Adr784.append("ApparentEnergyPlus_L3")
        self.Adr784.append("UInt64")
        self.Adr784.append(0)

        self.Adr788=[]
        self.Adr788=[788]
        self.Adr788.append("ApparentEnergyMinus_L3")
        self.Adr788.append("UInt64")
        self.Adr788.append(0)        
        
        self.Adr8192=[]
        self.Adr8192 =[8192]
        self.Adr8192.append("ManufacturerID")
        self.Adr8192.append("UInt16")
        self.Adr8192.append(0) 
        

    #-----------------------------------------
    # Routine to read a string from one address with 8 registers 
    def ReadStr8(self,myadr_dec):   
        r1=self.client.read_holding_registers(myadr_dec,8,unit=71)
        STRG8Register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big)
        result_STRG8Register =STRG8Register.decode_string(8)      
        return(result_STRG8Register) 
    #-----------------------------------------
    # Routine to read a Float from one address with 2 registers     
    def ReadFloat(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,2,unit=71)
        FloatRegister = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        result_FloatRegister =round(FloatRegister.decode_32bit_float(),2)
        return(result_FloatRegister)   
    #-----------------------------------------
    # Routine to read a U16 from one address with 1 register 
    def ReadU16_1(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,1,unit=71)
        U16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        result_U16register = U16register.decode_16bit_uint()
        return(result_U16register)
    #-----------------------------------------
    # Routine to read a Int32 from one address with 1 register 
    def ReadInt32(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,2,unit=71)
        U32register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        result_U32register = U32register.decode_32bit_int()
        return(result_U32register)
    #-----------------------------------------
    # Routine to read a UInt64 from one address with 1 register 
    def ReadUInt64(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,4,unit=71)
        U64register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        result_U64register = U64register.decode_64bit_uint()
        return(result_U64register)
    #-----------------------------------------
    # Routine to read a U16 from one address with 2 registers 
    def ReadU16_2(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,2,unit=71)
        U16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        result_U16register = U16register.decode_16bit_uint()
        return(result_U16register)
    #-----------------------------------------
    # Routine to read a U32 from one address with 2 registers 
    def ReadU32(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,2,unit=71)
        #print ("r1 ", rl.registers)
        U32register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        #print ("U32register is", U32register)
        #result_U32register = U32register.decode_32bit_float()
        result_U32register = U32register.decode_32bit_uint()
        return(result_U32register)
    #-----------------------------------------
    def ReadU32new(self,myadr_dec):
        print ("I am in ReadU32new with", myadr_dec)
        r1=self.client.read_holding_registers(myadr_dec,2,unit=71)
        U32register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        result_U32register = U32register.decode_32bit_uint()
        return(result_U32register)
    #-----------------------------------------    
    # Routine to read a U32 from one address with 2 registers 
    def ReadS16(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,1,unit=71)
        S16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        result_S16register = S16register.decode_16bit_uint()
        return(result_S16register)
                          
        
    def run(self):
        self.statuslogger.info("Running")
        self.logger.info("Running")
        
        sendCounter = 0
        while True:
            self.statuslogger.info("Looping")
            sleep(1)

            try:        
                msgs = []

                self.client = ModbusTcpClient(self.ksem_hostname, port=self.ksem_port)            
                self.client.connect()

                # LONG List of reads...
                self.Adr0[3]=self.ReadU32(self.Adr0[0])*0.1
                self.Adr2[3]=self.ReadU32(self.Adr2[0])*0.1
                self.Adr4[3]=self.ReadU32(self.Adr4[0])*0.1
                self.Adr6[3]=self.ReadU32(self.Adr6[0])*0.1         
                self.Adr16[3]=self.ReadU32(self.Adr16[0])*0.1
                self.Adr18[3]=self.ReadU32(self.Adr18[0])*0.1               
                self.Adr24[3]=self.ReadInt32(self.Adr24[0])*0.001
                self.Adr26[3]=self.ReadU32(self.Adr26[0])*0.001 
                self.Adr40[3]=self.ReadU32(self.Adr40[0])*0.1
                self.Adr42[3]=self.ReadU32(self.Adr42[0])*0.1
                self.Adr44[3]=self.ReadU32(self.Adr44[0])*0.1
                self.Adr46[3]=self.ReadU32(self.Adr46[0])*0.1            
                self.Adr56[3]=self.ReadU32(self.Adr56[0])*0.1            
                self.Adr58[3]=self.ReadU32(self.Adr58[0])*0.1            
                self.Adr60[3]=self.ReadU32(self.Adr60[0])*0.001            
                self.Adr62[3]=self.ReadU32(self.Adr62[0])*0.001            
                self.Adr64[3]=self.ReadInt32(self.Adr64[0])*0.001  
                self.Adr80[3]=self.ReadU32(self.Adr80[0])*0.1            
                self.Adr82[3]=self.ReadU32(self.Adr82[0])*0.1              
                self.Adr84[3]=self.ReadU32(self.Adr84[0])*0.1              
                self.Adr86[3]=self.ReadU32(self.Adr86[0])*0.1              
                self.Adr96[3]=self.ReadU32(self.Adr96[0])*0.1              
                self.Adr98[3]=self.ReadU32(self.Adr98[0])*0.1              
                self.Adr100[3]=self.ReadU32(self.Adr100[0])*0.001              
                self.Adr102[3]=self.ReadU32(self.Adr102[0])*0.001
                self.Adr104[3]=self.ReadInt32(self.Adr104[0])*0.001            
                self.Adr120[3]=self.ReadU32(self.Adr120[0])*0.1           
                self.Adr122[3]=self.ReadU32(self.Adr122[0])*0.1            
                self.Adr124[3]=self.ReadU32(self.Adr124[0])*0.1            
                self.Adr126[3]=self.ReadU32(self.Adr126[0])*0.1             
                self.Adr136[3]=self.ReadU32(self.Adr136[0])*0.1
                self.Adr138[3]=self.ReadU32(self.Adr138[0])*0.1 
                self.Adr140[3]=self.ReadU32(self.Adr140[0])*0.001             
                self.Adr142[3]=self.ReadU32(self.Adr142[0])*0.001             
                self.Adr144[3]=self.ReadInt32(self.Adr144[0])*0.001             
                #self.Adr60[3]=self.ReadU32(self.Adr60[0])*0.001
                self.Adr512[3]=self.ReadUInt64(self.Adr512[0])*0.0001   
                self.Adr516[3]=self.ReadUInt64(self.Adr516[0])*0.0001       
                self.Adr520[3]=self.ReadUInt64(self.Adr520[0])*0.0001       
                self.Adr524[3]=self.ReadUInt64(self.Adr524[0])*0.0001                   
                self.Adr544[3]=self.ReadUInt64(self.Adr544[0])*0.0001
                self.Adr548[3]=self.ReadUInt64(self.Adr548[0])*0.0001
                self.Adr592[3]=self.ReadUInt64(self.Adr592[0])*0.0001           
                self.Adr596[3]=self.ReadUInt64(self.Adr596[0])*0.0001            
                self.Adr600[3]=self.ReadUInt64(self.Adr600[0])*0.0001            
                self.Adr604[3]=self.ReadUInt64(self.Adr604[0])*0.0001            
                self.Adr624[3]=self.ReadUInt64(self.Adr624[0])*0.0001            
                self.Adr628[3]=self.ReadUInt64(self.Adr628[0])*0.0001            
                self.Adr672[3]=self.ReadUInt64(self.Adr672[0])*0.0001            
                self.Adr676[3]=self.ReadUInt64(self.Adr676[0])*0.0001            
                self.Adr680[3]=self.ReadUInt64(self.Adr680[0])*0.0001            
                self.Adr684[3]=self.ReadUInt64(self.Adr684[0])*0.0001            
                self.Adr704[3]=self.ReadUInt64(self.Adr704[0])*0.0001          
                self.Adr708[3]=self.ReadUInt64(self.Adr708[0])*0.0001            
                self.Adr752[3]=self.ReadUInt64(self.Adr752[0])*0.0001            
                self.Adr756[3]=self.ReadUInt64(self.Adr756[0])*0.0001            
                self.Adr760[3]=self.ReadUInt64(self.Adr760[0])*0.0001            
                self.Adr764[3]=self.ReadUInt64(self.Adr764[0])*0.0001            
                self.Adr784[3]=self.ReadUInt64(self.Adr784[0])*0.0001            
                self.Adr788[3]=self.ReadUInt64(self.Adr788[0])*0.0001            
      
                self.Adr8192[3]=self.ReadU16_1(self.Adr8192[0])
            
                self.KostalRegister=[]
                self.KostalRegister.append(self.Adr0)
                self.KostalRegister.append(self.Adr2)
                self.KostalRegister.append(self.Adr4)
                self.KostalRegister.append(self.Adr6)           
                self.KostalRegister.append(self.Adr16)
                self.KostalRegister.append(self.Adr18)              
                self.KostalRegister.append(self.Adr24)                  
                self.KostalRegister.append(self.Adr26)
            
                self.KostalRegister.append(self.Adr40)            
                self.KostalRegister.append(self.Adr42)
                self.KostalRegister.append(self.Adr44)
                self.KostalRegister.append(self.Adr46)
                self.KostalRegister.append(self.Adr56)
                self.KostalRegister.append(self.Adr58)
                self.KostalRegister.append(self.Adr60)
                self.KostalRegister.append(self.Adr62)
                self.KostalRegister.append(self.Adr64)
                self.KostalRegister.append(self.Adr80)
                self.KostalRegister.append(self.Adr82)
                self.KostalRegister.append(self.Adr84)
                self.KostalRegister.append(self.Adr86)
                self.KostalRegister.append(self.Adr96)
                self.KostalRegister.append(self.Adr98)
                self.KostalRegister.append(self.Adr100)
                self.KostalRegister.append(self.Adr102)
                self.KostalRegister.append(self.Adr104)
                self.KostalRegister.append(self.Adr120)
                self.KostalRegister.append(self.Adr122)
                self.KostalRegister.append(self.Adr124)
                self.KostalRegister.append(self.Adr126)
                self.KostalRegister.append(self.Adr136)
                self.KostalRegister.append(self.Adr138)
                self.KostalRegister.append(self.Adr140)
                self.KostalRegister.append(self.Adr142)
                self.KostalRegister.append(self.Adr144)            
                #self.KostalRegister.append(self.Adr60)
                self.KostalRegister.append(self.Adr512) 
                self.KostalRegister.append(self.Adr516)     
                self.KostalRegister.append(self.Adr520)     
                self.KostalRegister.append(self.Adr524) 
                self.KostalRegister.append(self.Adr544)
                self.KostalRegister.append(self.Adr548)
                self.KostalRegister.append(self.Adr592)  
                self.KostalRegister.append(self.Adr596)  
                self.KostalRegister.append(self.Adr600)  
                self.KostalRegister.append(self.Adr604)              
                self.KostalRegister.append(self.Adr624)  
                self.KostalRegister.append(self.Adr628)  
                self.KostalRegister.append(self.Adr672)  
                self.KostalRegister.append(self.Adr676)
                self.KostalRegister.append(self.Adr680)  
                self.KostalRegister.append(self.Adr684)  
                self.KostalRegister.append(self.Adr704)  
                self.KostalRegister.append(self.Adr708)
                self.KostalRegister.append(self.Adr752)  
                self.KostalRegister.append(self.Adr756)  
                self.KostalRegister.append(self.Adr760)  
                self.KostalRegister.append(self.Adr764)
                self.KostalRegister.append(self.Adr784)  
                self.KostalRegister.append(self.Adr788)  
            
                self.KostalRegister.append(self.Adr8192)
            
                self.client.close()

                counter = 0
                values = []
                if hasattr(self, 'KostalValuesOld') and sendCounter < 1200:
                    for elements in self.KostalRegister:
                        roundelementold = self.KostalValuesOld[counter]
                        counter = counter + 1
                        sendCounter = sendCounter + 1

                        roundelement = round(elements[3], 4)
                        values.append(roundelement)

                        if roundelement != roundelementold:
                            msgs.append({ "topic": self.mqtt_topic + elements[1], "payload": roundelement, "qos": self.mqtt_qos, "retain": self.mqtt_retain })
                else:
                    for elements in self.KostalRegister:
                        sendCounter = 0
                        roundelement = round(elements[3], 4)
                        values.append(roundelement)
                        msgs.append({ "topic": self.mqtt_topic + elements[1], "payload": roundelement, "qos": self.mqtt_qos, "retain": self.mqtt_retain })
                
                self.KostalValuesOld = values

                if len(msgs) > 0:
                    publish.multiple(msgs, hostname=self.mqtt_host, port=self.mqtt_port, client_id=self.mqtt_client_id, auth=self.mqtt_auth)

            except Exception as ex:
                self.logger.info("Exception: ", ex)
                pass
#-----------------------------


logging.basicConfig(stream=sys.stdout, format='%(asctime)s: %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.level = logging.INFO
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.handlers.RotatingFileHandler("/log/ksem-mqtt.log", maxBytes=10000000, backupCount=4)
handler.setFormatter(formatter)
logger.addHandler(handler)

statuslogger = logging.getLogger("status")
statuslogger.level = logging.INFO
statushandler = logging.handlers.RotatingFileHandler("/log/ksem-mqtt-status.log", maxBytes=1000000, backupCount=2)
statushandler.setFormatter(formatter)
statuslogger.addHandler(statushandler)

ksem = KsemMqtt()
ksem.init(logger, statuslogger)
ksem.logger = logger
ksem.statuslogger = statuslogger
ksem.run()
