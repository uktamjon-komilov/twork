class OtpService:
    def __init__(self, otp_obj):
        self.code = otp_obj.code
        self.phone = self._clean_phone(otp_obj.phone)
        self._execute()


    def _clean_phone(self, phone):
        from api.utils import clean_phone
        return clean_phone(phone)
    

    def _execute(self):
        from time import sleep
        sleep(2)
