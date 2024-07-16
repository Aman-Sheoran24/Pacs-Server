import os
import logging
from pydicom import dcmread
from pydicom.errors import InvalidDicomError
from pynetdicom import AE, StoragePresentationContexts, debug_logger

# Enable pynetdicom's debug logging
debug_logger()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('DICOM Sender')

# Path to the DICOM file you want to send
dicom_file_path = r'/home/vision_pac_server/Downloads/PAT034/D0001.dcm'

# Read the DICOM file with force=True
logger.debug(f'Reading DICOM file from {dicom_file_path}')
try:
    ds = dcmread(dicom_file_path, force=True)
except InvalidDicomError as e:
    logger.error(f'Invalid DICOM file: {e}')
    raise

# Create an AE instance
ae = AE()

# Add requested presentation contexts
ae.requested_contexts = StoragePresentationContexts

# Define the remote AE title, host, and port
remote_ae = ('0.0.0.0', 8000)  # IP and port of the machine running test_receive.py
remote_aet = 'MY_AE'  # AE title of the DICOM server

logger.debug(f'Attempting association with {remote_ae[0]}:{remote_ae[1]} with AE title {remote_aet}')
# Associate with the peer AE
assoc = ae.associate(remote_ae[0], remote_ae[1], ae_title=remote_aet)

if assoc.is_established:
    # Use the C-STORE service to send the DICOM file
    logger.debug(f'Association established, sending DICOM file {dicom_file_path}')
    status = assoc.send_c_store(ds)
    if status:
        logger.info(f'Successfully sent {dicom_file_path}')
    else:
        logger.error(f'Failed to send {dicom_file_path}')
    # Release the association
    assoc.release()
else:
    logger.error('Association failed')
