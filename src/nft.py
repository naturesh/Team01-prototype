
import requests
import json



def create_nft(uuid, agentName):

    resp = requests.post('https://mdoys95xl0.execute-api.ap-northeast-2.amazonaws.com/dev/register', data=json.dumps({
        'userAddress': '0xFdCEcEc5818E31E3e8f03Ab3FAc5EA7e6e380287' ,
        'uuid' : uuid,
        'agentName' : agentName
    }))


    # 제대로 되는지 체크 로직 
    return True


def verify_nft(uuid):

    resp = requests.post('https://mdoys95xl0.execute-api.ap-northeast-2.amazonaws.com/dev/verify', data=json.dumps({
        'uuid' : uuid,
    }))

    # 제대로 되는지 체크 로직 
    return True
   