# if len(reply_str) > 1024:
#     reply_str_t = f'''\uD83C\uDF89查询到{result_count}个结果\n✨机器人查询到结果：扣除{config.query_per_score}积分\n\n__内容过长，避免影响格式，转为文件发送__'''
#
#     file_name = fr'penguinSGK-{utils.generate_invite_code()}'
#     with open(f'reply_data/{file_name}.txt', 'w', encoding='utf8') as reply_file:
#         reply_file.write(reply_str.replace('*', '').replace('`', ''))
#     await client.send_message(sender, reply_str_t, reply_to=message_id, file=f'reply_data/{file_name}.txt')
#     # await client.send_message(sender, file='reply_data/test.txt')