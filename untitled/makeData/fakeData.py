from faker import Faker
fake = Faker("zh-cn")
for _ in range(10):
    data = fake.ipv6()
    print(data)
