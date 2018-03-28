from contextlib import contextmanager
from datetime import datetime
import time
import boto3


@contextmanager
def track_time(processor_name, action, message, bucket, folder):
    """
    Function to measure time execution.

    :param processor_name: Process name. Type = String.
    :param action: Action which will be executed. Type = String.
    :param message: Additional info. Type = String.
    :param bucket: S3 bucket name. Type = String.
    :param folder: place on S3 where to save CSV files. Type = String.
    """
    t0 = time.time()
    yield

    try:
        exec_time = time.time() - t0
        record = '{processor},{action},{message},{execution_time},{datetime}'\
            .format(processor=processor_name,
                    action=action,
                    message=message,
                    execution_time=round(exec_time, 4),
                    datetime=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    )

        # Upload CSV to S3
        file_name = '{processor}-{action}-{timestamp}.csv'.format(processor=processor_name,
                                                                  action=action,
                                                                  timestamp=datetime.utcnow()
                                                                  .strftime("%Y-%m-%d-%H-%M-%S-%f"))
        s3 = boto3.resource('s3')
        s3.Object(bucket, folder + '/' + file_name).put(Body=record, ServerSideEncryption='AES256')
    except Exception as details:
        print(details)
