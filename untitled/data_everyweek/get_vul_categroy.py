import constans
import common_model

# 漏洞分类的路径
vul_cate_url = '/asset-svc/loopholeCategory/list'
url = constans.PROD_URL + vul_cate_url

data = {
  "categoryName": "",
  "type": 1
}
vul_list = common_model.send_post_request(url, data,constans.PROD_TOKEN)
# print (vul_list)

num_check = common_model.count_key_value_pairs_in_json(vul_list,'isAutoCheck',1)
print(f'已开启自动审核的漏洞分类数量:{num_check}')
num_review = common_model.count_key_value_pairs_in_json(vul_list,'autoReview',1)
print(f'已开启自动复测的漏洞分类数量:{num_review}')