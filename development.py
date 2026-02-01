from faker import Faker

# Khởi tạo Faker
fake = Faker()


def generate_fake_emails(count: int, domain: str = '@example.com'):
    """Tạo một danh sách các địa chỉ email giả lập."""
    emails = []

    for i in range(count):
        # Tạo tên người dùng (username) ngẫu nhiên
        # Faker đảm bảo username là duy nhất và an toàn
        username = fake.user_name()

        # Kết hợp để tạo email
        email = f"{username}{domain}"
        emails.append(email)

    return emails


# Tạo 2000 email giả với đuôi @example.com
NUM_EMAILS = 2000
fake_emails = generate_fake_emails(NUM_EMAILS, domain='@example.com')

print(f"Đã tạo {len(fake_emails)} email giả lập thành công (ví dụ: {fake_emails[0]})")

# Nếu bạn muốn lưu ra file:
with open("fake_emails.txt", "w") as f:
    for email in fake_emails:
        f.write(email + "\n")
