import math
import time


class Calculate_ETO(object):

   def __calculate_eto__(self, results, alt,lat ):
        """
        Based upon the reference http://www.cimis.water.ca.gov/Content/PDF/CIMIS%20Equation.pdf
        Actual solar radiation used
        albedo of .18 used
        no cloud cover assumed
        """
        alt = alt * 0.3048
        pressure = 101.3-(.0115*alt)+(5.44*(10**-7)*alt*alt) #Step 5
        ETod = 0
        day_of_year = time.localtime().tm_yday
        dr = 1 + .033 * math.cos(2 * 3.14159 / 365 * day_of_year)
        delta = .409 * math.sin(2 * 3.14159 / 365 * day_of_year - 1.39)
        lat = 3.14159 / 180 * lat

        for i in results:
                # ETo COMPUTATIONAL PROCEDURE
                # The CIMIS Penman Equation was developed for use with hourly weather data. Required input data for the ETo computation include hourly means of air temperature (Ta; units of degrees C), vapor
                # pressure deficit (VPD; units of kilopascals: kPa), wind speed (U2; units of m/s), and net radiation (Rn: units of mm/hr of equivalent evaporation). Hourly values of ETo (EToh) in mm/hr are
                # computed using the following:
                #EToh = W*Rn + (1-W)*VPD*FU2              (1)
                # where W is a dimensionless partitioning factor, and FU2 is an empirical wind function (units: mm/hr/kPa). Daily values of ETo are computed by simply summing the twenty-four hourly EToh
                # values computed from Eq. 1 for the period ending at midnight (end of AZMET day). Specific computational procedures used to obtain the required parameters for Eq. 1 are provided below.
                # Net Radiation (Rn)
                # CIMIS originally measured Rn using instruments known as net radiometers. CIMIS abandoned the use of net radiometers in the early 1990s for a variety of reasons. AZMET chose not use net
                # radiometers and has computed hourly net radiation since network inception (1986) using a simple, clear sky estimation procedure that uses solar radiation (SR) expressed in units of MJ/m*m/hr
                # and mean hourly vapor pressure (ea; units: kPa). The
                # procedure is provided below:
            P = pressure
            U2 = i["wind_speed"]
           

            tc = i["TC"]
            tk = tc + 273.3   #Step 1
            es = .6108 * math.exp(17.27 * tc / (tk)) # Step 2 vapor pressure Tetens equation
            ea = es * i["HUM"] / 100.
            VPD = es - ea # vapor pressure deficient # Step 3

            DEL = (4099*es)/((tc+237.3)*(tc+237.3)) #Step # 4
            G = 0.000646 * P * (1 + 0.000949 * tc)  # Step 6

            W = DEL/(DEL+G)
            
            # For Daytime Conditions (SR>=0.21 MJ/m*m/hr):

            SR = i["SolarRadiationWatts/m^2"]
            #
            # Wind Function Step 8
            #
            if SR > 10: 
                FU2 = 0.03 + 0.0576 * U2

            else:  # For Nighttime Conditions (SR<0.21 MJ/m*m/hr):

                FU2 = 0.125 + 0.0439 * U2

            #SETP 9
            SR = .82 * SR # .18 for decidous trees

            NR = SR / (694.5 * (1 - 0.000946 * tc)) # Step 10
            #
            # tk is radiation from ground to sky
            # 273 is temperature of sky
            # ignoring cloulds
            RL = -5.67*(10**-8)*(273**4) + 5.67*(10**-8)*(tk**4) 
            
            RL = RL / (694.5 * (1 - 0.000946 * tc))
            ETRL = W * RL

            ETH = NR*W +(1-W)*VPD*FU2 -ETRL

            ETH = ETH*24  # equations are per hour we are using %day so multiply by 24 to normalize to hour

            
            
            ETod = ETod + (ETH*i["delta_timestamp"])
        print(ETod/25.4)
        return ETod / 25.4