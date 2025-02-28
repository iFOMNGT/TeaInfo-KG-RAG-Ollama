import os
import stat
import shutil

def save_backup() -> None:
    
    # 列出目录下的所有文件和目录
    entries = os.listdir('/home/lct/LightRAG/Backup')

    # 按修改时间排序
    # sorted_entries = list(sorted(entries, key=lambda x: os.stat(os.path.join('/home/lct/LightRAG/Backup', x)).st_mtime))
    sorted_entries = list(sorted(entries))
    print(sorted_entries)
    lastest_version = int(sorted_entries[-1].replace("version", ""))
    print(lastest_version)



    # 源目录路径
    source_directory = '/home/lct/LightRAG/output'
    # 目标目录路径
    destination_directory = f'/home/lct/LightRAG/Backup/version{lastest_version+1}'

    # 复制目录
    shutil.copytree(source_directory, destination_directory)

if __name__=='__main__':
    save_backup()