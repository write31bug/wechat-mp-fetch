import sys
sys.path.insert(0, r'E:\openclaw\tasks')
from task_board import create_task, get_task

result = create_task('T006', 'SQLite并发测试-Writer', '小金', '背景：测试writer能否同时写入数据库；目标：验证不冲突')
print('创建结果:', result)

t = get_task('T006')
print('查询结果:', t)
