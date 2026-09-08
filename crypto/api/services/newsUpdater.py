# import time
#
# from .news_service import update_news
#
#
# class NewsUpdater:
#
#     def __init__(self):
#         self.interval = 60 * 15  # 15 minutes
#
#     def run(self):
#
#         print("News updater started")
#
#         while True:
#
#             try:
#                 print("Updating news...")
#
#                 update_news()
#
#                 print("News updated successfully")
#
#             except Exception as e:
#                 print("News updater error:", e)
#
#             time.sleep(self.interval)