import urllib
import urllib2
import logging
import xml.sax
import datetime
import base64
import hashlib

logger = logging.getLogger(__name__)

MERCHANT_ID = "656873"
PASS_KEY = "12f57a17731e3c4be06836adfbdfe2550dfd440bc8cf3e378415f237ce6494f6"
CALLBACK_URL = "https://api.briskpesa.com/v1/onlinecheckout"
MPESA_CHECKOUT_URL = "https://safaricom.co.ke/mpesa_online/lnmo_checkout_server.php?wsdl"
#MPESA_CHECKOUT_URL = "http://localhost:8080" # for testing

class ProcessCheckOutResponseHandler(xml.sax.ContentHandler):
   def __init__(self):
      self.CurrentData = ""
      self.RETURN_CODE = ""
      self.DESCRIPTION = ""
      self.TRX_ID = ""
      self.ENC_PARAMS = ""
      self.CUST_MSG = ""

   # Call when an element starts
   def startElement(self, tag, attributes):
      self.CurrentData = tag

   # Call when an elements ends
   def endElement(self, tag):
      self.CurrentData = ""

   # Call when a character is read
   def characters(self, content):
      if self.CurrentData == "RETURN_CODE":
         self.RETURN_CODE = content
      elif self.CurrentData == "DESCRIPTION":
         self.DESCRIPTION = content
      elif self.CurrentData == "TRX_ID":
         self.TRX_ID = content
      elif self.CurrentData == "ENC_PARAMS":
         self.ENC_PARAMS = content
      elif self.CurrentData == "CUST_MSG":
         self.CUST_MSG = content

class TransactionStatusResponseHandler(xml.sax.ContentHandler):
   def __init__(self):
      self.CurrentData = ""
      self.MSISDN = ""
      self.AMOUNT = ""
      self.MPESA_TRX_DATE = ""
      self.MPESA_TRX_ID = ""
      self.TRX_STATUS = ""
      self.RETURN_CODE = ""
      self.DESCRIPTION = ""
      self.TRX_ID = ""

   # Call when an element starts
   def startElement(self, tag, attributes):
      self.CurrentData = tag

   # Call when an elements ends
   def endElement(self, tag):
      self.CurrentData = ""

   # Call when a character is read
   def characters(self, content):
      if self.CurrentData == "MSISDN":
         self.MSISDN = content
      elif self.CurrentData == "AMOUNT":
         self.AMOUNT = content
      elif self.CurrentData == "MPESA_TRX_DATE":
         self.MPESA_TRX_DATE = content
      elif self.CurrentData == "MPESA_TRX_ID":
         self.MPESA_TRX_ID = content
      elif self.CurrentData == "TRX_STATUS":
         self.TRX_STATUS = content
      elif self.CurrentData == "RETURN_CODE":
         self.RETURN_CODE = content
      elif self.CurrentData == "DESCRIPTION":
         self.DESCRIPTION = content
      elif self.CurrentData == "TRX_ID":
         self.TRX_ID = content

class ConfirmTransactionResponseHandler(xml.sax.ContentHandler):
   def __init__(self):
      self.CurrentData = ""
      self.RETURN_CODE = ""
      self.DESCRIPTION = ""
      self.TRX_ID = ""

   # Call when an element starts
   def startElement(self, tag, attributes):
      self.CurrentData = tag

   # Call when an elements ends
   def endElement(self, tag):
      self.CurrentData = ""

   # Call when a character is read
   def characters(self, content):
      if self.CurrentData == "RETURN_CODE":
         self.RETURN_CODE = content
      elif self.CurrentData == "DESCRIPTION":
         self.DESCRIPTION = content
      elif self.CurrentData == "TRX_ID":
         self.TRX_ID = content


class ProcessCallbackHandler(xml.sax.ContentHandler):
   def __init__(self):
      self.CurrentData = ""
      self.MERCHANT_TRANSACTION_ID = ""
      self.MPESA_TRX_DATE = ""
      self.MPESA_TRX_ID = ""
      self.AMOUNT = ""
      self.TRX_STATUS = ""
      self.RETURN_CODE = ""
      self.DESCRIPTION = ""
      self.TRX_ID = ""
      self.ENC_PARAMS = ""
      self.MSISDN = ""

   # Call when an element starts
   def startElement(self, tag, attributes):
      self.CurrentData = tag

   # Call when an elements ends
   def endElement(self, tag):
      self.CurrentData = ""

   # Call when a character is read
   def characters(self, content):
      if self.CurrentData == "MERCHANT_TRANSACTION_ID":
         self.MERCHANT_TRANSACTION_ID = content
      elif self.CurrentData == "MPESA_TRX_DATE":
         self.MPESA_TRX_DATE = content
      elif self.CurrentData == "MPESA_TRX_ID":
         self.MPESA_TRX_ID = content
      elif self.CurrentData == "AMOUNT":
         self.AMOUNT = content
      elif self.CurrentData == "TRX_STATUS":
         self.TRX_STATUS = content
      elif self.CurrentData == "RETURN_CODE":
         self.RETURN_CODE = content
      elif self.CurrentData == "DESCRIPTION":
         self.DESCRIPTION = content
      elif self.CurrentData == "TRX_ID":
         self.TRX_ID = content
      elif self.CurrentData == "ENC_PARAMS":
         self.ENC_PARAMS = content
      elif self.CurrentData == "MSISDN":
         self.MSISDN = content

def parser_process_checkout_response(xml_string):
   processCheckOutResp = ProcessCheckOutResponseHandler()
   xml.sax.parseString(xml_string, processCheckOutResp)
   return processCheckOutResp

def parser_transaction_status_response(xml_string):
   transactionStatusResp = TransactionStatusResponseHandler()
   xml.sax.parseString(xml_string, transactionStatusResp)
   return transactionStatusResp

def parser_confirm_transaction_response(xml_string):
   confirmTransactionResp = ConfirmTransactionResponseHandler()
   xml.sax.parseString(xml_string, confirmTransactionResp)
   return confirmTransactionResp

def parser_process_callback(xml_string):
   processCallback = ProcessCallbackHandler()
   xml.sax.parseString(xml_string, processCallback)
   return processCallback

def encryptPassword(timestamp):
  return base64.b64encode(hashlib.sha256(MERCHANT_ID + PASS_KEY + timestamp).hexdigest())

def send_payment_request(msisdn, amount, reqid, refid):
    # build the xml request
    xml_string = build_payment_xml(msisdn, reqid, refid, amount)
    #logger.info("Payment request XML: " + xml_string)
    xml_resp = ""
    try:
        req = urllib2.Request(url=MPESA_CHECKOUT_URL, data=xml_string, headers={'Content-Type': 'application/xml'})
        resp = urllib2.urlopen(req)
        if resp.getcode() == 200:
           xml_resp = resp.read()
        else:
            logger.error("Bad http status code: " + str(resp.getcode()))
    except Exception as e:
        logger.error("Error " + str(e))

    logger.info("Payment response XML: " + xml_resp)
    if (xml_resp != ""):
       p = parser_process_checkout_response(xml_resp)
       return p.RETURN_CODE, p.DESCRIPTION, p.TRX_ID, p.ENC_PARAMS, p.CUST_MSG
    else:
       return -1,

def build_payment_xml(msisdn, transaction_id, reference_id, amount):
    '''Build the XML file given the template and the parameters'''
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = encryptPassword(timestamp)
    XML = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="tns:ns">
        <soapenv:Header>
          <tns:CheckOutHeader>
            <MERCHANT_ID>%s</MERCHANT_ID>
            <PASSWORD>%s</PASSWORD>
            <TIMESTAMP>%s</TIMESTAMP>
          </tns:CheckOutHeader>
        </soapenv:Header>
        <soapenv:Body>
          <tns:processCheckOutRequest>
            <MERCHANT_TRANSACTION_ID>%s</MERCHANT_TRANSACTION_ID>
            <REFERENCE_ID>%s</REFERENCE_ID>
            <AMOUNT>%s</AMOUNT>
            <MSISDN>%s</MSISDN>
            <ENC_PARAMS></ENC_PARAMS>
            <CALL_BACK_URL>%s</CALL_BACK_URL>
            <CALL_BACK_METHOD>xml</CALL_BACK_METHOD>
            <TIMESTAMP>%s</TIMESTAMP>
          </tns:processCheckOutRequest>
        </soapenv:Body>
        </soapenv:Envelope>"""
    return XML % (MERCHANT_ID, password, timestamp, transaction_id, reference_id, amount, msisdn, CALLBACK_URL, timestamp)

def send_status_request(trx_id):
    # build the xml request
    xml_string = build_status_xml(trx_id)
    xml_resp = ""
    try:
        req = urllib2.Request(url=MPESA_CHECKOUT_URL, data=xml_string, headers={'Content-Type': 'application/xml'})
        resp = urllib2.urlopen(req)
        if resp.getcode() == 200:
           xml_resp = resp.read()
        else:
            logger.error("Bad http status code: " + str(resp.getcode()))
    except Exception as e:
         logger.error("Error " + str(e))
    if (xml_resp != ""):
       p = parser_transaction_status_response(xml_resp)
       return p.MSISDN, p.AMOUNT, p.MPESA_TRX_DATE, p.MPESA_TRX_ID, p.TRX_STATUS, p.RETURN_CODE, p.DESCRIPTION, p.TRX_ID
    else:
       return -1,

def build_status_xml(trx_id):
    '''Build the XML file given the template and the parameters'''
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = encryptPassword(timestamp)
    XML = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="tns:ns">
        <soapenv:Header>
          <tns:CheckOutHeader>
            <MERCHANT_ID>%s</MERCHANT_ID>
            <PASSWORD>%s</PASSWORD>
            <TIMESTAMP>%s</TIMESTAMP>
          </tns:CheckOutHeader>
        </soapenv:Header>
        <soapenv:Body>
          <tns:transactionStatusRequest>
      <TRX_ID>%s</TRX_ID>
          </tns:transactionStatusRequest>
        </soapenv:Body>
        </soapenv:Envelope>"""
    return XML % (MERCHANT_ID, password, timestamp, trx_id)


def send_confirm_request(trx_id):
    # build the xml request
    xml_string = build_confirm_xml(trx_id)
    #logger.info("Confirm request XML: " + xml_string)
    xml_resp = ""
    try:
        req = urllib2.Request(url=MPESA_CHECKOUT_URL, data=xml_string, headers={'Content-Type': 'application/xml'})
        resp = urllib2.urlopen(req)
        if resp.getcode() == 200:
           xml_resp = resp.read()
        else:
            logger.error("Bad http status code: " + str(resp.getcode()))
    except Exception as e:
         logger.error("Error " + str(e))

    logger.info("Confirm response XML: " + xml_resp)
    if (xml_resp != ""):
       p = parser_confirm_transaction_response(xml_resp)
       return p.RETURN_CODE, p.DESCRIPTION, p.TRX_ID
    else:
       return -1,


def build_confirm_xml(trx_id):
    '''Build the XML file given the template and the parameters'''
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = encryptPassword(timestamp)
    XML = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="tns:ns">
        <soapenv:Header>
          <tns:CheckOutHeader>
            <MERCHANT_ID>%s</MERCHANT_ID>
            <PASSWORD>%s</PASSWORD>
            <TIMESTAMP>%s</TIMESTAMP>
          </tns:CheckOutHeader>
        </soapenv:Header>
        <soapenv:Body>
          <tns:transactionConfirmRequest>
            <TRX_ID>%s</TRX_ID>
          </tns:transactionConfirmRequest>
        </soapenv:Body>
        </soapenv:Envelope>"""
    return XML % (MERCHANT_ID, password, timestamp, trx_id)