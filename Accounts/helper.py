
import requests
import json

registration_ids = "dZsqmpRIs0GCnSU1IXMlW8:APA91bHXtGJQW8AGSSAtdz0BOX12-xa6N1g-l-Ws7zZofr15YyDop_b16ix8A4XYhUTXbA9-Nb6IsitWLQHeITw1k7O0C5VzeVMFTOI0ybdt0ottH2MIWpAaW8JnqbthsKLxKY_xK13h"
message_title = "Hello You got"
message_desc = "Hello Testing"

def send_notification(registration_ids , message_title , message_desc , action , info_data):
    #fcm_api = "AAAAjG_ontY:APA91bG_pu05vhQm2IE4gGjOFjAC1mFtzZF0j_zsI_JQWl58u9LsLHnoEpjrLV5cIMNBPsVkFbf52zerKkhCc1Kj8wOEosMCKOtTG1_vE4Ji_pez9kKdxeA-9MLfItcnTrYWeN9grRw0"
    try:
        url = "https://fcm.googleapis.com/fcm/send"

        headers = {
            "Content-Type": "application/json",
            "Authorization": 'key=AAAAyREJETk:APA91bF_A0HV93gPZg2dw07h08E95i9rhZ9HZs6LhcGS46O2PU6pj7J8ao7uWn39iaHWLflJTBfXWX7fKavcA-0DlffGdw38mCzB_HjB3lMgmX0anlDdIJg7-FTf4nH4GD58KsqVPlPy',
        }

        payload = {
            "registration_ids" :registration_ids,
            "priority" : "high",
            "notification" : {
                "body" : message_desc,
                "title" : message_title,
                "image" : "https://shebirth.com/wp-content/uploads/2023/03/Untitled-design-30-1024x768.png",
                "icon": "https://shebirth.com/wp-content/uploads/2021/10/Shebirth-Final-Logo-new.png",
                "click_action" : action
            },
            "data" : info_data
        }

        print(payload)

        result = requests.post(url,  data=json.dumps(payload), headers=headers )
        print(result.text)
    
    except Exception as e:
        print(e)
        import sys, os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)



#send_notification(registration_ids , message_title , message_desc ,action="criticality")