# Copyright (c) 2022, malnoziliye@gmail.com	 and contributors
# For license information, please see license.txt
# from tkinter.messagebox import NO
import xmltodict
import json
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_path
from frappe.core.doctype.file.file import get_files_in_folder
from datetime import date
from frappe.utils import getdate
from lxml import etree


class ImportXML(Document):
	def save(self, *args, **kwargs):
		if not self.is_new():
			self.save_xml_date()
		super().save(*args, **kwargs) # call the base save method

	def save_xml_date(self):
		if self.folder_import:
			file_list = self.get_folder_files("Home/"+self.folder)
			for i in file_list:
				if frappe.db.exists("OFP", frappe.get_site_path()+"/"+i.file_url):
					continue
				self.add_ofp_records(frappe.get_site_path()+"/"+i.file_url)
			
		else:
			file_path = frappe.get_site_path()+"/"+self.xml_file
			self.add_ofp_records(file_path)
		
	def get_folder_files(self, folder):
		files = frappe.db.get_list(
		"File",
		{"folder": folder},
		["file_url"]
		)
		return files


	def add_ofp_records(self, file_path):
		xtree = etree.parse(file_path)
		xroot = xtree.getroot()
		
		with open(file_path) as xml_file:
			data_dict = xmltodict.parse(xml_file.read())
		
		thisdict = {}
		thisdict["xml_file_path"] = file_path
		thisdict["ofpcomputedtime"] = data_dict["FlightPlan"]["@computedTime"]
		thisdict["flightplanid"] =  data_dict["FlightPlan"]["@flightPlanId"]
		thisdict["date"] = data_dict["FlightPlan"]["M633SupplementaryHeader"]["Flight"]["@flightOriginDate"]
		thisdict["dayofweek"] = date.isoweekday(getdate(thisdict["date"]))
		thisdict["flt_no"] = data_dict["FlightPlan"]["M633SupplementaryHeader"]["Flight"]["FlightIdentification"]["FlightNumber"]["@number"]
		
		thisdict["dep_icao"] = data_dict["FlightPlan"]["M633SupplementaryHeader"]["Flight"]["DepartureAirport"]["AirportICAOCode"]
		thisdict["arr_icao"] = data_dict["FlightPlan"]["M633SupplementaryHeader"]["Flight"]["ArrivalAirport"]["AirportICAOCode"]
		# + data_dict["FlightPlan"]["FuelHeader"]["AlternateFuels"]["EstimatedWeight"]["Value"]["@unit"] + " , "
		# + data_dict["FlightPlan"]["FuelHeader"]["AlternateFuels"]["FinalReserve"]["EstimatedWeight"]["Value"]["#text"]+" "
		# + data_dict["FlightPlan"]["FuelHeader"]["AlternateFuels"]["FinalReserve"]["EstimatedWeight"]["Value"]["@unit"]

		thisdict["arr_iata"] = data_dict["FlightPlan"]["M633SupplementaryHeader"]["Flight"]["DepartureAirport"]["AirportIATACode"]

		# thisdict["Altn1 IATA"] = ["FlightPlan"]["M633SupplementaryHeader"]["Flight"]["ArrivalAirport"]["AirportICAOCode"]
		thisdict["reg"] = data_dict["FlightPlan"]["M633SupplementaryHeader"]["Aircraft"]["@aircraftRegistration"]
		thisdict["type"] = data_dict["FlightPlan"]["M633SupplementaryHeader"]["Aircraft"]["AircraftModel"]["AircraftICAOType"]
		thisdict["std"] = data_dict["FlightPlan"]["M633SupplementaryHeader"]["Flight"]["@scheduledTimeOfDeparture"]
		thisdict["sta"] = data_dict["FlightPlan"]["FlightPlanSummary"]["ScheduledTimeOfArrival"]
		thisdict["blk"] = data_dict["FlightPlan"]["FlightPlanSummary"]["BlockTime"]["EstimatedTime"]["Value"]
		thisdict["ofp_perffactor"] = data_dict["FlightPlan"]["FlightPlanHeader"]["PerformanceFactor"]
		thisdict["ofp_trip_ff"] = ' '.join((data_dict["FlightPlan"]["FlightPlanHeader"]["FuelFlowInformation"]["AverageFuelFlow"]["Value"]["#text"],
		data_dict["FlightPlan"]["FlightPlanHeader"]["FuelFlowInformation"]["AverageFuelFlow"]["Value"]["@unit"]))

		# """
		# data_dict["FlightPlan"]["FlightPlanHeader"]["FuelFlowInformation"]["AverageFuelFlow"]["Value"]["#text"] 
		#  $data_dict["FlightPlan"]["FlightPlanHeader"]["FuelFlowInformation"]["AverageFuelFlow"]["Value"]["@unit"]
		
		# """
		#' '.join(("string1","string2","stringN"))

		

		thisdict["ofp_hold_ff"] = ' '.join((data_dict["FlightPlan"]["FlightPlanHeader"]["FuelFlowInformation"]["HoldingFuelFlow"]["Value"]["#text"],
		data_dict["FlightPlan"]["FlightPlanHeader"]["FuelFlowInformation"]["HoldingFuelFlow"]["Value"]["@unit"]))
		
		thisdict["ofp_ci"] = data_dict["FlightPlan"]["FlightPlanHeader"]["RouteInformation"]["CruiseProcedure"]["@procedure"]
		
		thisdict["ofp_trip_time"] = data_dict["FlightPlan"]["FuelHeader"]["TripFuel"]["Duration"]["Value"]
		thisdict["ofp_trip_fuel"] =' '.join((data_dict["FlightPlan"]["FuelHeader"]["ContingencyFuel"]["EstimatedWeight"]["Value"]["#text"],
		data_dict["FlightPlan"]["FuelHeader"]["ContingencyFuel"]["EstimatedWeight"]["Value"]["@unit"]))
		

		thisdict["ofp_cont_time"] = data_dict["FlightPlan"]["FuelHeader"]["ContingencyFuel"]["Duration"]["Value"]
		# thisdict["OFP Altn Fuel"] = ' '.join((data_dict["FlightPlan"]["FuelHeader"]["AlternateFuels"]["AlternateFuel"]["EstimatedWeight"]["Value"]["#text"],
		# data_dict["FlightPlan"]["FuelHeader"]["AlternateFuels"]["AlternateFuel"]["EstimatedWeight"]["Value"]["#@unit"]))
		
		# thisdict["OFP Altn Time"] = data_dict["FlightPlan"]["FuelHeader"]["AlternateFuels"]["AlternateFuel"]["Duration"]["Value"]
		# thisdict["Final Resv. 30 min"] = data_dict["FlightPlan"]["FuelHeader"]["AlternateFuels"]["AlternateFuel"]["FinalReserve"]["Duration"]["Value"]
		
		thisdict["extrafuel"] = None
		thisdict["tankering"] = None
		
		
		thisdict["maximumfuelweight"] = ' '.join(( data_dict["FlightPlan"]["FuelHeader"]["PossibleExtraFuel"]["MaximumFuelWeight"]["Weight"]["Value"]["#text"],
		data_dict["FlightPlan"]["FuelHeader"]["PossibleExtraFuel"]["MaximumFuelWeight"]["Weight"]["Value"]["@unit"]))
		

		thisdict["takeofffuel"] = ' '.join((data_dict["FlightPlan"]["FuelHeader"]["TakeOffFuel"]["EstimatedWeight"]["Value"]["#text"],
		data_dict["FlightPlan"]["FuelHeader"]["TakeOffFuel"]["EstimatedWeight"]["Value"]["@unit"]))
		

		thisdict["takeofffuel_t"] = data_dict["FlightPlan"]["FuelHeader"]["TakeOffFuel"]["Duration"]["Value"]
		thisdict["taxifuel"] = ' '.join((data_dict["FlightPlan"]["FuelHeader"]["TaxiFuel"]["EstimatedWeight"]["Value"]["#text"],
		data_dict["FlightPlan"]["FuelHeader"]["TaxiFuel"]["EstimatedWeight"]["Value"]["@unit"]))
	
		thisdict["taxitime"] = data_dict["FlightPlan"]["FuelHeader"]["TaxiFuel"]["Duration"]["Value"]

		thisdict["blockfuel"] =' '.join((data_dict["FlightPlan"]["FuelHeader"]["BlockFuel"]["EstimatedWeight"]["Value"]["#text"],
		data_dict["FlightPlan"]["FuelHeader"]["BlockFuel"]["EstimatedWeight"]["Value"]["@unit"]))
	

		thisdict["blockfueltime"] = data_dict["FlightPlan"]["FuelHeader"]["BlockFuel"]["Duration"]["Value"]

		thisdict["arrivalfuel"] = ' '.join(( data_dict["FlightPlan"]["FuelHeader"]["ArrivalFuel"]["EstimatedWeight"]["Value"]["#text"],
		data_dict["FlightPlan"]["FuelHeader"]["ArrivalFuel"]["EstimatedWeight"]["Value"]["@unit"]))
		
		#You display this fuel minus the trip fuel and then divid it by 1000 so that we get the value of one kg
		thisdict["deltazfw"] =None

		thisdict["ofp_dow"] = ' '.join((data_dict["FlightPlan"]["WeightHeader"]["DryOperatingWeight"]["EstimatedWeight"]["Value"]["#text"],
		data_dict["FlightPlan"]["WeightHeader"]["DryOperatingWeight"]["EstimatedWeight"]["Value"]["@unit"]))
		
		
		thisdict["payload"] = ' '.join((data_dict["FlightPlan"]["WeightHeader"]["Load"]["EstimatedWeight"]["Value"]["#text"],
		data_dict["FlightPlan"]["WeightHeader"]["Load"]["EstimatedWeight"]["Value"]["@unit"]))	
		thisdict["ofp_ezfw"] = ' '.join((data_dict["FlightPlan"]["WeightHeader"]["ZeroFuelWeight"]["EstimatedWeight"]["Value"]["#text"],
		data_dict["FlightPlan"]["WeightHeader"]["ZeroFuelWeight"]["EstimatedWeight"]["Value"]["@unit"]))
		
		thisdict["ofp_dyn_tow"] = ' '.join((data_dict["FlightPlan"]["WeightHeader"]["ZeroFuelWeight"]["OperationalLimit"]["Value"]["#text"],
		data_dict["FlightPlan"]["WeightHeader"]["ZeroFuelWeight"]["OperationalLimit"]["Value"]["@unit"]))
		
		thisdict["ofp_dyn_ldw"] =' '.join((data_dict["FlightPlan"]["WeightHeader"]["LandingWeight"]["OperationalLimit"]["Value"]["#text"],
		 data_dict["FlightPlan"]["WeightHeader"]["LandingWeight"]["OperationalLimit"]["Value"]["@unit"]))
		

		#data_dict[""][""][""][""][""][""]
		# print("here")
		# print(data_dict["FlightPlan"]["FuelHeader"]["AlternateFuels"]["AlternateFuel"]["Airport"]["AirportICAOCode"])
		# for i in data_dict["FlightPlan"]["FuelHeader"]["AlternateFuels"]["AlternateFuel"]["Airport"]["AirportICAOCode"]:
		# 	print(i)
		# thisdict["altn1_icao"] = xroot.findall('.//{*}FuelHeader/{*}AlternateFuels/{*}AlternateFuel/{*}Airport/{*}AirportICAOCode')[0].text
		
		# thisdict["altn2_icao"] = xroot.findall('.//{*}FuelHeader/{*}AlternateFuels/{*}AlternateFuel/{*}Airport/{*}AirportICAOCode')[1].text
		# thisdict["altn2_fuel"] = None
		# thisdict["altn3_icao"] = xroot.findall('.//{*}FuelHeader/{*}AlternateFuels/{*}AlternateFuel/{*}Airport/{*}AirportICAOCode')[2].text
		# thisdict["altn3_fuel"] = None
		# thisdict["altn4_icao"] = xroot.findall('.//{*}FuelHeader/{*}AlternateFuels/{*}AlternateFuel/{*}Airport/{*}AirportICAOCode')[3].text
		# thisdict["altn4_fuel"] = None

		# thisdict["FSR OUT"] = data_dict[""][""][""][""][""][""]
		# thisdict["FSR OFF"] = data_dict[""][""][""][""][""][""]
		# thisdict["FSR ON"] = data_dict[""][""][""][""][""][""]
		# thisdict["FSR IN"] = data_dict[""][""][""][""][""][""]
		# #multiply the number by 100
		# thisdict["FSR OUT FUEL"] = data_dict[""][""][""][""][""][""]
		# thisdict["FSR OFF FUEL"] = data_dict[""][""][""][""][""][""]
		# #This is due to the low accuracy of the ACARS for takeoff we would like to cacaulate it as follows: FSR off fuel - taxi out fuel should be the Caculated FSR off fuel
		# thisdict["Caculated FSR OFF FUEL"] = data_dict[""][""][""][""][""][""]
		# thisdict["FSR ON FUEL"] = data_dict[""][""][""][""][""][""]
		# #This is due to the low accuracy of the ACARS for landing we would like to cacaulate it as follows: FSR on fuel plus taxi in fuel should be the Caculated FSR off fuel
		# thisdict["Caculated FSR on FUEL"] = data_dict[""][""][""][""][""][""]
		# thisdict["FSR IN FUEL"] = data_dict[""][""][""][""][""][""]
		# thisdict["LS EDNO"] = data_dict[""][""][""][""][""][""]
		# thisdict["LS DOW"] = data_dict[""][""][""][""][""][""]
		# thisdict["Payload"] = data_dict[""][""][""][""][""][""]
		# thisdict["LS ZFW"] = data_dict[""][""][""][""][""][""]
		# thisdict["LS T/OFF FUEL"] = data_dict[""][""][""][""][""][""]
		# thisdict["LS Block FUEL"] = data_dict[""][""][""][""][""][""]
		


		# OFPComputedTime = 
		# print(data_dict["FlightPlan"]["M633SupplementaryHeader"]["Flight"]["@flightOriginDate"])
		# for k,FlightPlan in data_dict.items():
		# 	print("k ", k, "  ", "v ", )
		# for k_tables, tables in FlightPlan.items():
		# 	print("k_tables ", k_tables, "tables", tables,"\n")
		# for k_col01, col01 in tables.items():
		# 	print("k_col01 ", k_col01, col01)
	

		# json_data = json.dumps(data_dict)
		# print(json_data)

		# for i in json_data:
		# 	print("i", i)

		# with open("data.json", "w") as json_file:
		# 		json_file.write(json_data)




		thisdict["xml_import"] = self.name

		doc = frappe.new_doc("OFP")
		doc.update(thisdict)
		doc.insert()
		# return thisdict
