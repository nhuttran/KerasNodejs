import os
import logging
import ftplib
from ftplib import FTP
from contextlib import closing
from ..Dto.RequestWorker import AuthTrainDto, RequestWorkerDto

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

def download_file(save_path_file, auth_train_dto=AuthTrainDto):
    logging.info("download_file_from_ftp START")

    try:
        with closing(ftplib.FTP()) as ftp:
            ftp.set_debuglevel(1)
            ftp.connect(auth_train_dto.ftpHost, int(auth_train_dto.ftpPort), int(60*2))
            ftp.login(auth_train_dto.ftpUserId, auth_train_dto.ftpPassword)
            train_path = os.path.dirname(auth_train_dto.downloadPathFile)
            train_file = os.path.basename(auth_train_dto.downloadPathFile)

            ftp.cwd(train_path)
            ftp.set_pasv(True)
            with open(save_path_file, 'wb') as file:
                res = ftp.retrbinary(f'RETR {train_file}', file.write)
                if not res.startswith('226 Transfer complete'):
                    logging.info("ファイルのダウンロードが終了できません. [%s]" % auth_train_dto.downloadPathFile)
                    os.remove(save_path_file)
            # FTP接続クローズ
            ftp.quit()
    except Exception as e:
        logging.info("例外エラーが発生しました。 {}".format(e))
        return False
    return True

def upload_file(auth_train_json_str, upload_path_file_list):
    auth_train_dto = AuthTrainDto.from_json_str(auth_train_json_str)
    try:
        with closing(ftplib.FTP()) as ftp:
            ftp.set_debuglevel(1)
            ftp.connect(auth_train_dto.ftpHost, int(auth_train_dto.ftpPort), int(60 * 2))
            ftp.login(auth_train_dto.ftpUserId, auth_train_dto.ftpPassword)
            ftp.cwd(auth_train_dto.uploadPath)
            ftp.set_pasv(True)
            for upload_path_file in upload_path_file_list:
                file_name = os.path.basename(upload_path_file)
                with open(upload_path_file, 'rb') as file:
                    # アップロード実行
                    ftp.storbinary(f'STOR {file_name}', file)
                    os.remove(upload_path_file)
    except Exception as e:
        logging.info("例外エラーが発生しました。 {}".format(e))
        return False
    return True

if __name__ == "__main__":
    pass