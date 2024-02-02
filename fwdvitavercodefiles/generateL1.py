from pymongo import MongoClient
import boto3
import time
from generatel1_v21 import *
from email_sender1 import emailSender

jobsCollection = None
s3 = None
bucketName = None
cluster = None

receiver_email = 'staffing@vitaver.com'
# receiver_email = 'aanchal.goel2508@gmail.com'

sender = emailSender()
sender.setup()


def connectToDBandS3():
    global jobsCollection,s3,bucketName, cluster

    cluster = MongoClient(
            "mongodb+srv://marina:gqTFE1S0fwr8goGZ@cluster0.u75kq1t.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp")

    jobsCollection = cluster['vitaver']['jobs']

    bucketName = "vitavers3bucket"

    s3 = boto3.client('s3', aws_access_key_id='AKIA265QHS6RBURYM5PA',
                               aws_secret_access_key='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')


def fetchLatestJobs():
    query = {"job_status": "new"}
    # Fetch documents that match the query
    result = jobsCollection.find(query)
    return result

def fetchFilefromS3(s3_key):
    mylocalpath = s3_key.replace("JD/","WIP_JD/")
    # print("MyLocalPath",mylocalpath)
    try:
        s3.download_file(bucketName, s3_key,mylocalpath)
        # print(f"File downloaded from S3 to {mylocalpath}")
    except Exception as e:
        print(f"An error occurred: {e}")

def saveFileToS3(local_path,s3_key):
    try:
        s3.upload_file(local_path, bucketName, s3_key)
        # print(f"File uploaded to S3 at {s3_key}")
    except Exception as e:
        print(f"An error occurred: {e}")
    



connectToDBandS3()
while True:
    jobs=fetchLatestJobs()

    # for job in jobs:
    #     value_to_print = job.get("client_system")
    #     print("Value from the document:", value_to_print)

    if jobs:
        s3_keys = []

        for job in jobs:

            if 'l1_status' not in job:
                jds = job.get("JDs")  # Get the JDs array from the document

                if 'client_id' in job:
                    client_id = int(job.get("client_id"))
                elif 'organization_id' in job:
                    client_id = int(job.get("organization_id"))



                for jd in jds:
                    if len(jd):
                        is_jd = jd.get("is_jd", None)
                        if is_jd==True:
                            s3_key = jd.get("s3_key", None)  # Get the "s3_key" value from the JD object
                            
                            if s3_key:
                                # print(s3_key)
                                fetchFilefromS3(s3_key)
                                print("🟢Now generating L1...")
                                jd_path = s3_key.replace("JD/","WIP_JD/")
                                l1_path = s3_key.replace("JD/","L1_Generated/")
                                l1_path = l1_path.replace(".pdf",".docx")
                                l1_s3_key = l1_path.replace("L1_Generated/","L1/L1_")
                                # run_and_extract_L1(jd_path,l1_path)
                                try:
                                    email_subject, pathToL1 = process_jd_l1(filename = jd_path, filename_output=l1_path, clientid=client_id)
                                    print(email_subject)

                                    L1 = [l1_path]
                                    sender.sendMail(receiver_email,'AI Test - '+email_subject,'The L1 is attached.',L1)
                                    print("🟢🟢🟢L1 Emailed.")
                                    saveFileToS3(l1_path,l1_s3_key)
                                    print("🟢🟢🟢L1 Saved on Cloud.")

                                    result = jobsCollection.update_one(
                                        {"message_id": job['message_id']},
                                        {"$set": {"l1_status": "Created"}}
                                    )
                                except:
                                    print("Some issue with L1 generation. Will try again after some time.")

                            # s3_keys.append(s3_key)
                        else:
                            print("Not a JD")
                pass
            else:
                pass
    else:
        print("No new jobs. Wating for 1 min.")


    print("Now Wating for 1 min.")
    time.sleep(5) #Sleep for 1 min
    






    




