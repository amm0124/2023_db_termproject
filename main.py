import psycopg2
from datetime import datetime, timezone, timedelta,time
import smtplib
from tabulate import tabulate
from email.mime.text import MIMEText
import sys
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression

user_con = None #로그인 한 유저별 connection 할당

def return_owner_connect():
    con = psycopg2.connect(
        database='termproject',
        user='db2023',
        password='db!2023',
        host='::1',
        port='5432'
    )
    return con


def welcome():
    print("************************************************************")
    print("********************쇼핑몰에 오신 것을 환영합니다****************")
    print("************************************************************")
    inp = input("신규 회원이면 1번, 기존 회원이면 2번을 입력해주세요 : ").strip()

    if inp == '1':
        print("회원 가입을 시작합니다.")
        create_account()
    elif inp == '2':
        print("반갑습니다 회원님.")
        print("로그인 페이지로 이동합니다.")
        login()
    else:
        print("[경고] 잘못된 입력입니다. ")
        count = 1
        while True:
            inp = input("신규 회원이면 1번, 기존 회원이면 2번을 입력해주세요 : ").strip()
            print(f"[경고] 남은 횟수 : {5 - count}회 남았습니다. ")
            if inp == '1':
                print("회원 가입 페이지로 넘어갑니다!")
                create_account()
                break
            elif inp == '2':
                print("반갑습니다 회원님!")
                login()
                break
            else:
                count += 1
                if count > 5:
                    print("[경고] 5회 초과된 잘못 된 입력을 감지했습니다. 프로그램을 종료합니다.")
                    sys.exit()
def create_account():
    con = return_owner_connect()
    cursor = con.cursor()
    exists_id = []
    type = input("일반 회원으로 가입을 원하시면 1번, 판매자로 가입을 원하시면 2번, 관리자로 가입을 원하시면 3번, 프로그램 종료를 원하시면 나머지 버튼을 눌러주세요 : ").strip()
    if type=='1' or type == '2' or type =='3' :
        type=int(type)
        if type == 1:  # customer
            cursor.execute("SELECT customer_id FROM customer_table")
            exists_id = cursor.fetchall()
        elif type == 2:  # seller
            cursor.execute("SELECT seller_id FROM seller_table")
            exists_id = cursor.fetchall()
        else:  # admin
            cursor.execute("SELECT administor_id FROM administor_table")
            exists_id = cursor.fetchall()

        print("회원가입을 위한 ID와 password를 입력해주세요.")
        print("ID는 이메일 형식으로 입력해야 합니다. 이메일 형식으로 입력하지 않을 시, 가입이 제한됩니다.")
        count = 0

        while True:
            id = input("ID : ").strip()
            if '@' not in id:
                print("[경고] 잘못된 입력입니다. 이메일 형식으로 id를 입력해주세요")
                print(f"[경고] 남은 횟수 : {5 - count}회 남았습니다. ")
                count += 1
                if count == 5:
                    print("[경고] @ 형식을 사용해주세요. 잘못 된 입력 5회 초과로 1분 후 입력 가능합니다.")
                    time.sleep(1000)
                    count = 0
            else:
                if (id,) in exists_id:
                    print("[경고] 존재하는 id입니다. 재입력해주세요.")
                else:
                    print("정상적으로 입력받았습니다.")
                    break

        temp_password = input("password : ").strip()
        password = input("다시 비밀번호를 입력해주세요 : ").strip()
        count = 1

        while True:
            if temp_password == password:
                break
            else:
                print("[경고] 초기 비밀번호와 동일하게 입력해주세요. ")
                password = input("다시 비밀번호를 입력해주세요. ").strip()
                count += 1
                if count > 3:
                    print("[경고] 비정상적인 가입이 감지되었습니다. 프로그램을 강제종료합니다.")
                    sys.exit()
        print("회원 정보를 데이터베이스에 저장중 ....")

        if type == 1:  # customer
            address_want = input("주소와 키, 몸무게의 입력을 원하시면 1번, 원하지 않는다면 그 외 버튼을 눌러주세요 :  ").strip()
            if address_want == '1':
                while True:
                    print("주소와, 키(정수), 몸무게(정수)를 입력해주세요 : ")
                    address = input("주소: ").strip()
                    height = input("키 : ").strip()
                    weight = input("몸무게 : ").strip()
                    if height.isdigit() and weight.isdigit():
                        print("정상적으로 입력되었습니다!")
                        break
                    else:
                        print("[경고] 키와 몸무게를 정수 형태로 입력해주세요!")
                cursor.execute(f"INSERT INTO customer_table VALUES('{id}', '{password}', 0, False ,'{address}' , {height}, {weight});")
            else:
                cursor.execute(f"INSERT INTO customer_table (customer_id, customer_pw, point, vip) VALUES('{id}', '{password}', 0, False); ")
        elif type == 2:  # seller
            cursor.execute(f"INSERT INTO seller_table (seller_id, seller_pw) VALUES('{id}', '{password}')")
        else:  # admin
            cursor.execute(f"INSERT INTO administor_table (administor_id, administor_pw) VALUES('{id}', '{password}')")

        con.commit()
        print("회원가입 완료!")
        print("시작 페이지로 돌아갑니다!")
        welcome()
    else :
        print("잘못된 입력입니다. 프로그램을 종료합니다.")

def login():
    type = input(("고객으로 로그인하시려면 1번, 판매자로 로그인하시려면 2번, 관리자로 로그인 하시려면 3번, 프로그램을 종료하시려면 그 외 입력을 해주세요. ")).strip()
    count = 0
    con = return_owner_connect()
    cursor = con.cursor()

    if type == '1':  # customer
        print("고객 로그인!")
        cursor.execute("select customer_id, customer_pw from customer_table")
        id_pw_pair = cursor.fetchall()
        print("[공지] 로그인을 하기 위한 ID와 password를 입력해주세요. ")
        id = input("ID: ").strip()
        password = input("password : ").strip()
        while True:
            if (id, password) in id_pw_pair:
                print("************로그인 성공**********")
                print("고객 메인 페이지로 넘어갑니다!")
                break
            else:
                if count == 5:
                    print("[경고] 비정상적인 로그인 접근입니다. 프로그램을 종료하겠습니다.")
                    sys.exit()
                else:
                    print("[경고] 존재하지 않는 회원입니다.")
                    print(f"[경고] 남은 횟수 : {5 - count}회 남았습니다. ")
                    id = input("ID: ")
                    password = input("password : ")
                    count += 1
        cursor.execute(f"SELECT * FROM customer_table WHERE customer_id='{id}'")  # postgresql에서 query where '' 문자열
        customer_information = cursor.fetchall()  # [('test1@naver.com', 'test1', 102000, False, '경상북도 의성군 단촌면 구계1길 18-4 37320 한국', 185, 75)]
        customer_main(customer_information[0])  # ('test1@naver.com', 'test1', 102000, False, '경상북도 의성군 단촌면 구계1길 18-4 37320 한국', 185, 75)
    elif type == '2':  # seller
        print("판매자 로그인!")
        cursor.execute("select seller_id, seller_pw from seller_table")
        id_pw_pair = cursor.fetchall()
        print("[공지] 로그인을 하기 위한 ID와 password를 입력해주세요")
        id = input("ID: ")
        password = input("password : ")
        while True:
            if (id, password) in id_pw_pair:
                print("************로그인 성공**********")
                print("판매자 메인 페이지로 넘어갑니다!")
                break
            else:
                if count == 5:
                    print("[경고] 비정상적인 로그인 접근입니다. 프로그램을 종료하겠습니다.")
                    sys.exit()
                else:
                    print("[경고] 존재하지 않는 회원입니다.")
                    print(f"[경고] 남은 횟수 : {5 - count}회 남았습니다. ")
                    id = input("ID: ")
                    password = input("password : ")
                    count += 1
        seller_main(id)
    elif type == '3':
        print("관리자 로그인!")
        cursor.execute("select administor_id, administor_pw from administor_table")
        id_pw_pair = cursor.fetchall()
        print("[공지] 로그인을 하기 위한 ID와 password를 입력해주세요")
        id = input("ID: ")
        # password = getpass.getpass("Enter your password: ")
        password = input("password : ")
        while True:
            if (id, password) in id_pw_pair:
                print("************로그인 성공**********")
                print("판매자 메인 페이지로 넘어갑니다!")
                break
            else:
                if count == 5:
                    print("[경고] 비정상적인 로그인 접근입니다. 프로그램을 종료하겠습니다.")
                    sys.exit()
                else:
                    print("[경고] 존재하지 않는 회원입니다.")
                    print(f"[경고] 남은 횟수 : {5 - count}회 남았습니다. ")
                    id = input("ID: ")
                    password = input("password : ")
                    count += 1

        administor_main(id)
    else:
        print("프로그램을 종료하겠습니다!")
        sys.exit()

# 고객 -----------------------------------------------------------------

def print_customer_main_page():
    print("--------회원 메인 페이지입니다!---------")
    print("1번을 누르면 포인트를 충전할 수 있습니다.")
    print("2번을 누르면 주문 조회 및 환불을 할 수 있습니다.")
    print("3번을 누르면 개인 정보를 수정할 수 있습니다.")
    print("4번을 누르면 품목 구매를 할 수 있습니다.")  # 장바구니 , 여기서 추천 시스템, 리뷰 조회 가능
    print("5번을 누르면 QnA 게시판으로 이동합니다.")
    print("6번을 누르면 이벤트 참여를 할 수 있습니다.")
    print("7번을 누르면 리뷰 등록을 할 수 있습니다.")
    print("8번을 누르면 장바구니 사용을 할 수 있습니다.")
    print("9번을 누르면 사이즈 추천을 받을 수 있습니다.")
    print("그 외를 누르면 프로그램을 종료합니다.")

def customer_main(customer_info):
    # ('test1@naver.com', 'test1', 102000, False, '경상북도 의성군 단촌면 구계1길 18-4 37320 한국', 185, 75,0)
    global user_con
    user_con = psycopg2.connect(
        database='termproject',
        user='customer',
        password='customer1',
        host='::1',
        port='5432'
    )
    cursor = user_con.cursor()
    customer_id = customer_info[0]
    vip = customer_info[3]
    cursor.execute(f"select point from customer_table where customer_id = '{customer_id}';")
    point = cursor.fetchall()
    point = point[0][0]
    print_customer_main_page()

    if vip:
        print(f"안녕하십니까. {customer_id} 회원님. 현재 회원님은 VIP 회원입니다. ")
    else:
        print(f"안녕하십니까. {customer_id} 회원님. 현재 회원님은 일반 회원입니다. ")
    print(f"고객님의 현재 포인트는 {point}입니다.")

    user_input = input("입력 : ").strip()

    if user_input == '1':  # 포인트 충전
        charging_point(customer_id)  # id 넘겨줌
    elif user_input == '2':  # 주문 조회 및 환불
        buying_item_lookup(customer_id)
    elif user_input == '3':  # 개인 정보 수정 및 탈퇴
        fix_my_account(customer_id, 1)  # id를 매개변수로 넘겨줌, type == 1 -> 고객으로 encoding
    elif user_input == '4':  # 품목 구매 (장바구니 ,추천 시스템)
        buying_item(customer_id)
    elif user_input == '5':  # QNA게시판
        QnA(customer_id)
    elif user_input == '6':  # 이벤트 참여
        event_join(customer_id)
    elif user_input == '7':  # 리뷰 등록
        review(customer_id)
    elif user_input=='8': #장바구니 사용
        wishlist(customer_id)
    elif user_input=='9':
        recommended_size(customer_id)
    else:
        print("프로그램을 종료합니다.")
        sys.exit()
    customer_main(customer_info)
def charging_point(customer_id):
    global user_con
    print("포인트 충전 페이지입니다!")

    while True:
        want_charging_point = input("충전하고 싶은 포인트를 입력하세요 : ")
        if want_charging_point.isdigit():
            break
        else:
            print("잘못된 입력입니다. 정수형으로 입력하세요. ")

    want_charging_point = int(want_charging_point)

    cursor = user_con.cursor()
    update_query = f"UPDATE customer_table SET point = point + {want_charging_point} WHERE customer_id = '{customer_id}';"
    cursor.execute(update_query)
    user_con.commit()
    print("포인트 충전 완료! 메인 페이지로 이동합니다.")


# 내가 샀던 품목 조회 및 리뷰 남기기
def buying_item_lookup(customer_id):
    global user_con
    print("구매 내역 조회입니다.")
    cursor = user_con.cursor()
    select_query = f"select * from order_review_table where customer_id='{customer_id}' ; "
    cursor.execute(select_query)
    my_buying_product = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame(my_buying_product, columns=columns)
    print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

    customer_input = input("환불하고자 하는 품목이 있으시다면 1번, 메인 페이지로 돌아가기를 원하신다면 그 외 다른 버튼을 입력해주세요 : ").strip()
    if customer_input == "1":
        print("환불을 시작합니다.")
        want_refund_product_order_code = input("환불하고자 하는 품목의 주문 번호를 입력해주세요 : ").strip()
        want_refund_product_count = (input("환불하고자 하는 품목의 수량을 정확하게 입력해주세요 : ")).strip()

        try:
            cursor.execute("BEGIN; ")
            current_time = datetime.now(timezone.utc)
            select_query = f"SELECT order_start_time, count, price_per_1, product_subcode FROM order_review_table WHERE order_code={want_refund_product_order_code} ;"
            cursor.execute(select_query)
            order_information = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            df = pd.DataFrame(order_information, columns=columns)
            print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

            order_start_time = order_information[0][0].replace(tzinfo=timezone.utc)
            order_product_count = order_information[0][1]
            one_per_price = order_information[0][2]
            subcode = order_information[0][3]
            remain_time = order_start_time - current_time
            enable_refund = remain_time.days < 7
            want_refund_product_count = int(want_refund_product_count)

            if want_refund_product_count > order_product_count:
                print("주문했던 수량보다 더 많은 입력입니다.")
                print("메인 페이지로 돌아갑니다.")
                return
            else:
                if enable_refund:

                    select_query = f"select vip from customer_table where customer_id='{customer_id}'"
                    cursor.execute(select_query)
                    is_vip = cursor.fetchall()
                    is_vip =is_vip[0][0]
                    print("환불을 시작합니다 ..")

                    update_query = f"UPDATE order_review_table SET count = count - {want_refund_product_count} WHERE order_code = {want_refund_product_order_code};"
                    cursor.execute(update_query)
                    print("구매 기록 변경 완료 ..")

                    if is_vip :
                        update_query = f"UPDATE customer_table SET point = point + {(one_per_price * want_refund_product_count)-3000} where customer_id ='{customer_id}';"
                    else :
                        update_query = f"UPDATE customer_table SET point = point + {(one_per_price * want_refund_product_count)-1000} where customer_id ='{customer_id}';"
                    cursor.execute(update_query)
                    print("금액 추가 완료..")

                    update_query = f"UPDATE customer_table SET acc_use_money = acc_use_money -  {one_per_price * want_refund_product_count} where customer_id ='{customer_id}';"
                    cursor.execute(update_query)
                    print("누적 금액 차감 완료..")

                    select_query= f"SELECT acc_use_money FROM customer_table WHERE customer_id ='{customer_id}';"
                    cursor.execute(select_query)
                    acc_money = cursor.fetchall()

                    update_query = f"UPDATE sub_product SET product_count = product_count + {want_refund_product_count} Where subcode= {subcode}"
                    cursor.execute(update_query)


                    if acc_money[0][0]<10000000 :
                        update_query = f"UPDATE customer_table SET vip = False where customer_id ='{customer_id}';"
                        cursor.execute(update_query)

                    user_con.commit()
                    print("환불이 완료되었습니다.")
                else:
                    print("일주일 이상 시간이 지나서 환불 불가능입니다.")
                    print("메인 페이지로 돌아갑니다.")
                    return

        except Exception as e:
            cursor.execute("ROLLBACK;")
            print(f"error 발생 : {e}")
            print("잘못 입력되었습니다.")

    else:
        print("메인 페이지로 돌아갑니다.")
        return


# 고객 정보 수정 tuple arguments
def fix_my_account(user_id, type):
    global user_con
    if type == 1:  # 고객 정보 수정
        print("고객 정보 수정 페이지입니다!")
        print("1번을 누르면 ID 수정입니다.")
        print("2번을 누르면 비밀번호 수정입니다.")
        print("3번을 누르면 주소 수정입니다.")
        print("4번을 누르면 키를 수정합니다.")
        print("5번을 누르면 몸무게를 수정합니다.")
        print("6번을 누르면 회원 탈퇴를 진행합니다.")
        print("7번을 누르면 고객 메인 페이지로 이동합니다.")
        print("그 외 버튼을 누르면 프로그램을 종료합니다.")
        count = 0
        user_input = input("입력 : ").strip()
        cursor = user_con.cursor()
        if user_input == '1':  # 아이디 변경
            while True:
                cursor.execute("SELECT customer_id FROM customer_table")
                exists_customer_id = cursor.fetchall()
                update_id = input("변경을 원하는 ID를 입력하세요 : ").strip()
                if '@' not in update_id:
                    print("[경고] 잘못된 입력입니다. 이메일 형식으로 id를 입력해주세요")
                    print(f"[경고] 남은 횟수 : {5 - count}회 남았습니다. ")
                    count += 1
                    if count == 5:
                        print("[경고] 잘못 된 입력 5회 초과로 시스템을 종료합니다.")
                        sys.exit()
                else:  # @ 포함
                    if (update_id,) in exists_customer_id:
                        print("[경고] 존재하는 id입니다. 재입력해주세요.")
                    else:
                        print("정상적으로 입력받았습니다.")
                        break

            update_query = f"UPDATE customer_table SET customer_id = '{update_id}' WHERE customer_id = '{user_id}';"
            cursor.execute(update_query)
            user_con.commit()
            print(f"고객 ID를 {update_id}로 수정했습니다!")
            print("고객 메인 페이지로 이동합니다.")
        elif user_input == '2':  # 비밀번호 변경
            update_password = input("업데이트 하고 싶은 비밀번호를 입력하세요 : ")
            update_query = f"UPDATE customer_table SET customer_pw = '{update_password}' WHERE customer_id = '{user_id}';"
            cursor.execute(update_query)
            user_con.commit()
            print("비밀번호 변경 완료했습니다!")
            print("고객 메인 페이지로 이동합니다.")
        elif user_input == '3':  # 주소 변경
            update_address = input("변경하고자 하는 주소를 입력해주세요 : ")
            update_query = f"UPDATE customer_table SET customer_address = '{update_address}' WHERE customer_id = '{user_id}';"
            cursor.execute(update_query)
            user_con.commit()
            print("주소를 성공적으로 변경했습니다!")
            print("고객 메인 페이지로 이동합니다.")
        elif user_input == '4':  # 키 변경
            update_height = input("변경하고자 하는 키를 입력해주세요 : ")
            update_query = f"UPDATE customer_table SET customer_address = {update_height} WHERE customer_id = '{user_id}';"
            cursor.execute(update_query)
            user_con.commit()
            print("키를 성공적으로 변경했습니다!")
            print("고객 메인 페이지로 이동합니다.")
        elif user_input == '5':  # 몸무게 변경
            update_weight = input("변경하고자 하는 몸무게를 입력해주세요 : ")
            update_query = f"UPDATE customer_table SET customer_address = {update_weight} WHERE customer_id = '{user_id}';"
            cursor.execute(update_query)
            user_con.commit()
            print("몸무게를 성공적으로 변경했습니다!")
            print("고객 메인 페이지로 이동합니다.")
        elif user_input == '6':
            print("회원 탈퇴를 진행합니다. ")
            withdraw = input("정말 탈퇴를 원하시면 1번, 메인 페이지로 돌아가기를 원하시면 2번을 입력해주세요 : ").strip()

            if withdraw == "1":
                print("회원 탈퇴를 진행합니다.")
                print("고객님의 정보는 삭제되지만, 고객님의 주문과, 리뷰는 ID가 가려진 채 남습니다. ")
                try:
                    delete_query = f"DELETE FROM CUSTOMER_TABLE WHERE customer_id='{user_id}' ;"
                    cursor.execute(delete_query)
                    user_con.commit()
                    print("탈퇴를 완료하였습니다..... 프로그램을 종료합니다.")
                    sys.exit()
                except Exception as e:
                    print(f"error 발생 : {e}")
                    print("프로그램을 종료합니다.")
                    sys.exit()
            else:
                print("고객 메인 페이지로 돌아갑니다")
        elif user_input == '7':
            print("고객 메인 페이지로 이동합니다.")
        else:
            print("프로그램을 종료합니다.")
            sys.exit()
    elif type == 2:  # 판매자 정보 수정
        print("판매자 정보 수정 페이지입니다!")
        print("1번을 누르면 ID 수정입니다.")
        print("2번을 누르면 비밀번호 수정입니다.")
        print("그 외 버튼을 누르면 프로그램을 종료합니다.")
        user_input = int(input("입력 : "))
        con = return_owner_connect()
        cursor = con.cursor()
        count = 0
        if user_input == 1:  # 판매자 아이디 변경
            while True:
                cursor.execute("SELECT seller_id FROM seller_table")
                exists_seller_id = cursor.fetchall()
                update_id = input("변경을 원하는 ID를 입력하세요 : ")
                if '@' not in update_id:
                    print("[경고] 잘못된 입력입니다. 이메일 형식으로 id를 입력해주세요")
                    print(f"[경고] 남은 횟수 : {5 - count}회 남았습니다. ")
                    count += 1
                    if count == 5:
                        print("[경고] 잘못 된 입력 5회 초과로 시스템을 종료합니다.")
                        sys.exit()
                else:  # @ 포함
                    if (update_id,) in exists_seller_id:
                        print("[경고] 존재하는 id입니다. 재입력해주세요.")
                    else:
                        print("정상적으로 입력받았습니다.")
                        break
            update_query = f"UPDATE seller_table SET seller_id = '{update_id}' WHERE seller_id = '{user_id}';"
            cursor.execute(update_query)
            con.commit()
            print(f"판매자 ID를 {update_id}로 수정했습니다!")
            print("판매자 메인 페이지로 이동합니다.")
        elif user_input == 2:  # 판매자 비밀번호 변경
            update_password = input("업데이트 하고 싶은 비밀번호를 입력하세요 : ")
            update_query = f"UPDATE seller_table SET seller_pw = '{update_password}' WHERE seller_id = '{user_id}';"
            cursor.execute(update_query)
            con.commit()
            print("비밀번호 변경 완료했습니다!")
            print("판매자 메인 페이지로 이동합니다.")
    else:
        print("관리자 정보 수정 페이지입니다!")
        print("1번을 누르면 ID 수정입니다.")
        print("2번을 누르면 비밀번호 수정입니다.")
        print("그 외 버튼을 누르면 프로그램을 종료합니다.")
        user_input = int(input("입력 : "))
        con = return_owner_connect()
        cursor = con.cursor()
        count = 0
        if user_input == 1:  # 관리자 아이디 변경
            while True:
                cursor.execute("SELECT administor_id FROM administor_table")
                exists_admin_id = cursor.fetchall()
                update_id = input("변경을 원하는 ID를 입력하세요 : ")
                if '@' not in update_id:
                    print("[경고] 잘못된 입력입니다. 이메일 형식으로 id를 입력해주세요")
                    print(f"[경고] 남은 횟수 : {5 - count}회 남았습니다. ")
                    count += 1
                    if count == 5:
                        print("[경고] 잘못 된 입력 5회 초과로 시스템을 종료합니다.")
                        sys.exit()
                else:  # @ 포함
                    if (update_id,) in exists_admin_id:
                        print("[경고] 존재하는 id입니다. 재입력해주세요.")
                    else:
                        print("정상적으로 입력받았습니다.")
                        break
            update_query = f"UPDATE administor_table SET adminisotr_id = '{update_id}' WHERE administor_id = '{user_id}';"
            cursor.execute(update_query)
            con.commit()
            print(f"관리자 ID를 {update_id}로 수정했습니다!")
            print("관리자 메인 페이지로 이동합니다.")
        elif user_input == 2:  # 관리자 비밀번호 변경
            update_password = input("업데이트 하고 싶은 비밀번호를 입력하세요 : ")
            update_query = f"UPDATE administor_table SET administor_pw = '{update_password}' WHERE administor_id = '{user_id}';"
            cursor.execute(update_query)
            con.commit()
            print("비밀번호 변경 완료했습니다!")
            print("관리자 메인 페이지로 이동합니다.")


def buying_item(customer_id):
    global user_con
    print("구매 페이지로 이동합니다.")

    cursor = user_con.cursor()
    user_input = input("바로 구매를 원하시면 1번, 장바구니에 있는 물건 구매를 원하시면 2번, 뒤로 가기를 그 외 다른 버튼을 눌러주세요 : ")

    if user_input == '1':
        print("살 수 있는 품목 리스트를 불러옵니다 .. .")
        print("순서대로 재고번호, 상위 카테고리, 하위 카테고리, 상품 이름, 상품 설명, 사이즈, 색상, 1개당 가격, 남아있는 재고량, 판매자 연락처입니다")
        select_query = f"select * from product_view "
        cursor.execute(select_query)
        product_list = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(product_list, columns=columns)

        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

        buy_input = input("몇 번째 품목 구매를 원하시나요? ").strip()
        buy_want_index = int(buy_input) - 1  # index 초기화

        product_price = product_list[buy_want_index][7]
        want_amount = int(input("구매하고자 하는 수량을 입력해주세요 : "))
        want_buy_product_subcode = product_list[buy_want_index][0]
        want_buy_product_seller_id = product_list[buy_want_index][-1]
        if want_amount > product_list[buy_want_index][8]:
            print("남아있는 수량보다 많이 입력했습니다.")
            print("메인 페이지로 돌아갑니다.")
        else:
            print(f"{want_amount}개의 수량을 입력하였습니다.")
            point_query = f"select point from customer_table where customer_id = '{customer_id}';"
            cursor.execute(point_query)
            remain_point = cursor.fetchall()
            remain_point = remain_point[0][0]
            after_remain_point = remain_point - want_amount * product_price
            print(f"현재 고객님의 남아있는 잔고는 {remain_point}입니다.")

            if after_remain_point < 0:
                print("포인트가 부족합니다.")
                print("메인 페이지로 돌아갑니다.")
            else:
                print(f"결제 후 남아있는 포인트는 {after_remain_point}입니다.")
                buy_choice = input("구매를 원하시면 1번을, 원하지 않고 메인 페이지로 돌아가시려면 그 외를 입력해주세요 : ")
                if buy_choice == '1':
                    print("구매를 시작합니다.")
                    try:
                        # 등업 및 결제
                        cursor.execute("BEGIN;")
                        use_money_query = f"select acc_use_money from customer_table where customer_id = '{customer_id}';"
                        cursor.execute(use_money_query)
                        acc_use_money = cursor.fetchall()
                        acc_use_money = acc_use_money[0][0]

                        if acc_use_money + want_amount * product_price >= 1000000:
                            print("축하합니다! VIP 회원으로 등급업 됐습니다.")
                            update_query = f"UPDATE customer_table SET point = {after_remain_point + 3000}, acc_use_money = acc_use_money + {want_amount * product_price}, vip = true;"
                        else:  # 적립금
                            update_query = f"UPDATE customer_table SET point = {after_remain_point + 1000}, acc_use_money = acc_use_money + {want_amount * product_price};"
                        cursor.execute(update_query)
                        print("포인트 출금 완료 .. ")

                        # order_review_table에 정보 남기기 -> order code 발급하기

                        select_query = f"select order_code from order_review_table "
                        cursor.execute(select_query)
                        exists_order_code = cursor.fetchall()
                        order_code = 0
                        if exists_order_code ==[] :
                            order_code = 1000000001
                        else:
                            order_code = exists_order_code[-1][0] + 1
                        current_time = datetime.now()
                        insert_query = f"insert into order_review_table VALUES({order_code},'{want_buy_product_seller_id}', {want_buy_product_subcode} ,{want_amount}, {product_price}, '{customer_id}', '{current_time}') ; "
                        cursor.execute(insert_query)

                        update_query = f"UPDATE sub_product SET product_count = product_count - {want_amount} Where subcode ={want_buy_product_subcode}"
                        cursor.execute(update_query)
                        user_con.commit()
                        print("구매 완료!")
                    except Exception as e:
                        # 예외 발생 시 롤백
                        cursor.execute("ROLLBACK;")
                        print(f"트랜잭션 롤백: {e}")
                else:
                    print("메인 페이지로 돌아갑니다")
                    return
    elif user_input=='2' :
        print("장바구니에 있는 품목 구매를 시작하겠습니다.")
        print("장바구니에 있는 품목을 불러옵니다 .. .")
        select_query = f"SELECT * FROM wishlist WHERE customer_id='{customer_id}' ;"
        cursor.execute(select_query)
        wishlists = cursor.fetchall() #(customer_id, subcode, count)
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(wishlists, columns=columns)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

        print("장바구니에 있는 품목을 구매하겠습니다..")
        point_query = f"select point from customer_table where customer_id = '{customer_id}';"
        cursor.execute(point_query)
        remain_point = cursor.fetchall()
        remain_point = remain_point[0][0]
        print(f"현재 고객님의 남아있는 잔고는 {remain_point}입니다.")
        wishlist_total_price = 0

        for item in wishlists :
            subcode = item[1]
            select_query = f"select product_price FROM product_view WHERE subcode = {subcode} "
            cursor.execute(select_query)
            price_per_1 = cursor.fetchall()
            price_per_1 = price_per_1[0][0]
            wishlist_total_price += price_per_1*item[2]
        after_remain_point = remain_point - wishlist_total_price

        if after_remain_point < 0 :
            print("포인트가 부족합니다. 장바구니의 수량을 조절하거나, 포인트를 충전해주세요 .")
            print("메인으로 돌아갑니다.")
            return

        print("결제를 시작합니다...")
        try:
            # 등업 및 결제
            cursor.execute("BEGIN;")
            use_money_query = f"select acc_use_money from customer_table where customer_id = '{customer_id}';"
            cursor.execute(use_money_query)
            acc_use_money = cursor.fetchall()
            acc_use_money = acc_use_money[0][0]

            if acc_use_money + wishlist_total_price >= 1000000:
                print("축하합니다! VIP 회원으로 등급업 됐습니다.")
                update_query = f"UPDATE customer_table SET point = {after_remain_point + 3000}, acc_use_money = acc_use_money + {wishlist_total_price}, vip = true;"
            else:  # 적립금
                update_query = f"UPDATE customer_table SET point = {after_remain_point + 1000}, acc_use_money = acc_use_money + {wishlist_total_price};"
            cursor.execute(update_query)
            print("포인트 출금 완료 .. ")

            # order_review_table에 정보 남기기 -> order code 발급하기
            # wishlist에 있는 품목에 한해서 ..

            for item in wishlists :
                subcode = item[1]
                count = item[2]
                select_query = f"select product_price FROM product_view WHERE subcode = {subcode} "
                cursor.execute(select_query)
                price_per_1 = cursor.fetchall()
                price_per_1 = price_per_1[0][0]

                print("주문번호 발급중입니다 ..")
                select_query = f"select order_code from order_review_table "
                cursor.execute(select_query)
                exists_order_code = cursor.fetchall()
                order_code = 0
                if exists_order_code == []:
                    order_code = 1000000001
                else:
                    order_code = exists_order_code[0][-1] + 1
                current_time = datetime.now()

                select_query = f"select product_seller FROM product_view Where subcode={subcode}"
                cursor.execute(select_query)
                seller_id = cursor.fetchall()
                seller_id = seller_id[0][0]
                insert_query = f"insert into order_review_table VALUES({order_code},'{seller_id}', {subcode} ,{count}, {price_per_1}, '{customer_id}', '{current_time}') ; "
                cursor.execute(insert_query)

                update_query = f"UPDATE sub_product SET product_count = product_count - {count} Where subcode ={subcode}"
                cursor.execute(update_query)

            print("구매 완료!")
            user_con.commit()
        except Exception as e:
            # 예외 발생 시 롤백
            cursor.execute("ROLLBACK;")
            print(f"트랜잭션 롤백: {e}")
    else :
        print("메인 페이지로 돌아갑니다")

def wishlist(customer_id):
    global user_con
    cursor = user_con.cursor()

    print("장바구니에 담기 전, 살 수 있는 품목 리스트를 불러옵니다 .. .")
    print("순서대로 재고번호, 상위 카테고리, 하위 카테고리, 상품 이름, 상품 설명, 사이즈, 색상, 1개당 가격, 남아있는 재고량, 판매자 연락처입니다")
    select_query = f"select * from product_view "
    cursor.execute(select_query)
    product_list = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame(product_list, columns=columns)
    print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

    while True :
        type = input("장바구니에 품목을 담고 싶으시면 1번, 장바구니 기능을 그만 사용하고 싶으시면 2번을 눌러주세요 : ").strip()
        if type =='1' :
            try :
                wish_code = int(input("장바구니에 담고 싶은 재고번호를 입력해주세요 : ").strip())
                select_query = f"SELECT product_subcode FROM wishlist where customer_id='{customer_id}';"
                cursor.execute(select_query)
                my_wishlist_subcodes = cursor.fetchall()
                if (wish_code, ) in my_wishlist_subcodes :
                    print("장바구니에 품목이 있으므로 수량을 조절합니다.")
                    wish_count = int(input("조절하고 싶은 수량을 입력해주세요 : "))
                    select_query = f"SELECT count FROM wishlist where customer_id='{customer_id}' and product_subcode={wish_code};"
                    cursor.execute(select_query)
                    wishlist_in_count = cursor.fetchall()
                    wishlist_in_count = wishlist_in_count[0][0]
                    
                    if wishlist_in_count + wish_count < 0:
                        print("담은 품목은 0보다 크거나 같아야 합니다.")
                    elif wishlist_in_count + wish_count == 0:
                        print("0이 되었으므로 장바구니에서 삭제합니다")
                        delete_query = f"DELETE FROM wishlist WHERE product_subcode={wish_code} and customer_id ='{customer_id}';"
                        cursor.execute(delete_query)
                    else :
                        update_query= f"UPDATE wishlist SET count = count + {wish_count} WHERE customer_id ='{customer_id}' and product_subcode={wish_code}"
                        cursor.execute(update_query)
                else :
                    print("장바구니에 품목을 추가합니다")
                    wish_count = int(input("수량을 입력해주세요 : "))
                    if wish_count <= 0 :
                        print("0보다 큰 수를 입력해주세요.")
                    else :
                        select_query = f"INSERT INTO wishlist VALUES('{customer_id}', '{wish_code}', {wish_count});"
                        cursor.execute(select_query)
                user_con.commit()
                print("장바구니 수정을 완료했습니다.")
            except Exception as e :
                print(f"양식에 맞추어 입력해주세요 : {e}")
                wishlist_continue=input("계속 하기를 원하시면 1번, 장바구니 사용을 종료하길 원하시면 다른 버튼을 눌려주세요 : ").strip()
                if wishlist_continue!='1':
                    break
                else :
                    print("다시 장바구니 사용을 시작합니다.")
        else :
            print("장바구니 사용을 종료합니다.")
            print("메인 페이지로 돌아갑니다.")
            return
    print("메인 페이지로 돌아갑니다.")


def QnA(customer_id):
    global user_con
    cursor = user_con.cursor()

    q_input = input("QnA 질문을 보고 싶으시면 1번, 질문을 남기고 싶으시면 2번, 메인 페이지로 돌아가고 싶으시면 그 외 다른 버튼을 눌러주세요 : ").strip()
    if q_input=='1' :
        print("QnA 게시판을 불러옵니다 ..")
        select_query = f"select qna_num, product_subcode, question, answer from qna;"
        cursor.execute(select_query)
        product_list = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(product_list, columns=columns)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

    elif q_input=='2':
        print("살 수 있는 품목 리스트를 불러옵니다 .. .")
        print("순서대로 재고번호, 상위 카테고리, 하위 카테고리, 상품 이름, 상품 설명, 사이즈, 색상, 1개당 가격, 남아있는 재고량, 판매자 연락처입니다")

        select_query = f"select * from product_view "
        cursor.execute(select_query)
        product_list = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(product_list, columns=columns)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
        try :
            product_subcode = input("품목 재고번호를 입력해주세요 : ").strip()
            question = input("남기고 싶은 질문을 입력해주세요 : ").strip()
            select_query = f"SELECT product_seller FROM product_view WHERE subcode = {product_subcode}"
            cursor.execute(select_query)
            seller_id = cursor.fetchall()
            seller_id = seller_id[0][0]

            select_query = f"select qna_num from qna; "
            cursor.execute(select_query)
            qna_num_list = cursor.fetchall()
            qna_num = 0
            if qna_num_list == []:
                qna_num = 1
            else:
                qna_num= qna_num_list[-1][0] + 1

            insert_query = f"INSERT INTO qna VALUES ('{customer_id}' , {product_subcode} , '{question}' ,'{seller_id}' ,'', {qna_num});"
            cursor.execute(insert_query)
            user_con.commit()
            print("QnA 질문 등록이 완료됐습니다.")

        except Exception as e:
            print(f"error : {e}")
            print("잘못 입력했습니다.")
        else :
            pass
    print("메인 페이지로 돌아갑니다.")

def review(customer_id):
    global user_con
    cursor = user_con.cursor()
    type = input("리뷰 등록을 하시려면 1번, 리뷰 조회를 원하시면 2번, 메인 페이지로 돌아가기를 원하시면 3번을 눌러주세요 : ").strip()

    if type=='1':
        print("구매 내역을 조회입니다.")
        cursor = user_con.cursor()
        select_query = f"select * from order_review_table where customer_id='{customer_id}' ; "
        cursor.execute(select_query)
        my_buying_product = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(my_buying_product, columns=columns)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
        try :
            print("리뷰 등록을 시작합니다.")
            review_order_code = int(input("리뷰를 남기고 싶은 주문번호를 입력해주세요 : ").strip())
            review_point = input("별점입니다. 1~10 사이 정수를 입력해주세요  : ").strip()
            review_point = int(review_point)
            review_content = input("리뷰 내용을 입력해주세요 : ").strip()
            user_height = 0
            user_weight = 0
            flag = input(f"사용한 user의 키와 몸무게를 {customer_id}님의 키와 몸무게로 사용하시려면 1번, 직접 입력을 원하시면 그 외 버튼을 눌러주세요 : ")
            if flag=='1' :
                select_query = f"SELECT height, weight FROM customer_table WHERE customer_id='{customer_id}'"
                cursor.execute(select_query)
                infor = cursor.fetchall()
                user_height = infor[0][0]
                user_weight = infor[0][1]
                print(user_height, user_weight)
            else :
                user_height = int(input("사용자의 키를 정수 형태로 입력해주세요 : ").strip())
                user_weight = int(input("사용자의 몸무게를 정수 형태로 입력해주세요 : ").strip())

            update_query =f"UPDATE order_review_table SET review_point = {review_point}, review_content = '{review_content}',user_height ={user_height}, user_weight={user_weight} WHERE order_code={review_order_code}"
            cursor.execute(update_query)
            print("리뷰를 성공적으로 등록했습니다.")
            user_con.commit()
        except Exception as e:
            print(f"양식을 갖춰서 입력해주세요 : {e}")
            print("메인으로 돌아갑니다.")
            return
    elif type=='2':
        print("살 수 있는 품목 리스트를 불러옵니다 .. .")
        print("순서대로 재고번호, 상위 카테고리, 하위 카테고리, 상품 이름, 상품 설명, 사이즈, 색상, 1개당 가격, 남아있는 재고량, 판매자 연락처입니다")
        select_query = f"select * from product_view "
        cursor.execute(select_query)
        product_list = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(product_list, columns=columns)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
        try:
            want_review_code = input("리뷰를 보고싶은 품목의 재고번호를 입력해주세요 : ").strip()
            want_review_code = int(want_review_code)
            print("리뷰 조회를 시작합니다.")
            select_query = f"SELECT review_point, review_content FROM order_review_table WHERE product_subcode ={want_review_code} ;"
            cursor.execute(select_query)
            review_list = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            df = pd.DataFrame(review_list, columns=columns)
            print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
            user_con.commit()
        except Exception as e:
            print(f"양식을 갖춰서 입력해주세요 : {e}")
            print("메인으로 돌아갑니다.")
            return
    else :
        print("메인 페이지로 돌아갑니다.")


def event_join(customer_id):
    global user_con
    print("이벤트 참여 페이지입니다!")
    cursor = user_con.cursor()
    try:
        current_time = datetime.now()
        insert_query = f"INSERT INTO event_table VALUES('{customer_id}', '{current_time}');"
        cursor.execute(insert_query)
        user_con.commit()
        print("이벤트 참여가 완료됐습니다! ")
    except Exception as e:
        # print(f"Error: {e}")
        print("이미 참여한 회원입니다.")
    print("메인 페이지로 돌아갑니다.")


def recommended_size(customer_id):
    global user_con
    print("사이즈 추천 시스템입니다. 이때까지 리뷰를 기반으로 작동합니다.")
    cursor = user_con.cursor()
    select_query = "SELECT user_height, user_weight, review_point FROM order_review_table;"
    cursor.execute(select_query)
    data = cursor.fetchall()
    try :

        columns = ['height', 'weight', 'point']
        df = pd.DataFrame(data, columns=columns)
        X = df[['height', 'weight']]
        y = df['point']
        model = LinearRegression()
        model.fit(X, y)

        user_height = int(input("키를 정수형으로 입력하세요 : ").strip())
        user_weight = int(input("키를 정수형으로 입력하세요 : ").strip())

        new_data = [(user_height,user_weight)]
        new_df = pd.DataFrame(new_data, columns=['height', 'weight'])
        predictions = model.predict(new_df)

        if predictions[0] >= 7 :
            print("괜찮을 듯 합니다!")
        else :
            print("추천하지 않습니다.")

    except Exception as e:
        print(f"{e} 발생. 양식에 맞추어 입력해주세요.")
        print("메인으로 돌아갑니다.")


# --------------판매자---------
def print_seller_main_page():
    print("--------판매자 메인 페이지입니다!---------")
    print("1번을 누르면 품목을 추가할 수 있습니다.")
    print("2번을 누르면 품목을 수정할 수 있습니다.")
    print("3번을 누르면 QnA 게시판으로 이동할 수 있습니다.")
    print("4번을 누르면 물품 판매에 대한 정보 조회 및 집계 가능합니다.")
    print("5번을 누르면 정보 수정을 할 수 있습니다.")
    print("그 외를 누르면 프로그램을 종료합니다.")

def seller_main(seller_id):

    global user_con
    user_con = psycopg2.connect(
        database='termproject',
        user='seller',
        password='seller1',
        host='::1',
        port='5432'
    )

    print(f"{seller_id}님 반갑습니다.")
    print_seller_main_page()

    user_input = (input("입력 : "))
    if user_input == '1':  # 품목 추가
        add_product(seller_id)
    elif user_input == '2':
        fix_product_info(seller_id)
    elif user_input == '3':
        qna_answer(seller_id)
    elif user_input == '4':
        check_my_product(seller_id)
    elif user_input == '5':
        fix_my_account(seller_id, 2)
    else:
        print("프로그램을 종료합니다.")
        sys.exit()
    seller_main(seller_id)


def add_product(seller_id):
    cursor = user_con.cursor()
    choice = (input("품목 입고 페이지입니다. 정보 입력을 원하시면 1번, 원하지 않고 메인 페이지로 돌아가기를 원하시면 1을 제외한 버튼을 눌러주세요 : "))
    if choice == "1":
        flag = input("상위 제품군을 입력하고 싶으시면 1번, 바로 하위 품목을 등록하고 싶으시면 다른 버튼을 눌러주세요 : ").strip()
        if flag =='1' :
            print("상위 카테고리, 하위 카테고리, 상품 이름, 상품 설명을 입력해주세요 :")
            top_category = input("상위 카테고리 : ").strip()
            sub_category = input("하위 카테고리 : ").strip()
            product_name = input("상품 이름 : ").strip()
            product_explain = input("상품 설명 : ").strip()
            try:
                print("top_category_code를 발급중입니다 . .. ")
                cursor.execute("BEGIN;")
                cursor.execute("SELECT topcode FROM top_product")
                top_product_code = cursor.fetchall()

                if top_product_code == [] :
                    top_product_code =1
                else :
                    top_product_code = int(top_product_code[-1][0]) + 1  # 제일 마지막 정수 형태 반환

                insert_query = f"INSERT INTO top_product VALUES ( {(top_product_code)}, '{top_category}' ,'{sub_category}' , '{product_name}' ,'{product_explain}' , '{seller_id}');"
                cursor.execute(insert_query)
                print("상위 데이터 삽입 완료. ")
                user_con.commit()
                print(f"발급받은 상위 코드 : {top_product_code}" )
            except Exception as e:
                # 예외 발생 시 롤백
                print(f"에러 : {e}")
                cursor.execute("ROLLBACK;")
                print("메인 페이지로 돌아갑니다.")
                return

        print("하위 품목을 등록합니다 .. ")
        print("sub_category_code를 발급중입니다 . .. ")
        cursor.execute("SELECT subcode FROM code_mapping_table")
        subcode = cursor.fetchall()
        if subcode ==[] :
            subcode=2023000001
        else :
            subcode = int(subcode[-1][0]) + 1

        top_product_code=int(input("존재하는 제품군의 상위 코드를 입력해주세요 : ").strip())
        select_query = f"select topcode from top_product"
        cursor.execute(select_query)
        exists_topcode = cursor.fetchall()

        if (top_product_code, ) in exists_topcode :
            try :
                cursor.execute("BEGIN;")
                insert_query = f"INSERT INTO code_mapping_table VALUES ( {subcode}, {top_product_code} );"
                cursor.execute(insert_query)
                print("code mapping 완료. ")

                print("제품 사이즈, 컬러, 가격, 수량을 입력해주세요. : ")

                product_size = input("제품 사이즈 (S,M,L,XL로 구분해서 입력해주세요) : ").strip()
                product_color = input("제품 색상 : ").strip()
                product_price = int(input("제품 가격 : ").strip())
                product_count = int(input("제품 수량 : ").strip())

                insert_query = f"INSERT INTO sub_product VALUES ({subcode} , '{product_size}' , '{product_color}' , {product_price}, {product_count} );"
                print(insert_query)
                cursor.execute(insert_query)
                print("2차 데이터 삽입 완료.")

                cursor.execute("COMMIT;")
                print("데이터 삽입 완료!")
            except Exception as e:
                # 예외 발생 시 롤백
                print(f"에러 : {e}")
                cursor.execute("ROLLBACK;")
                print("메인 페이지로 돌아갑니다.")
                return
    else:
        print("판매자 메인 페이지로 돌아갑니다.")


def fix_product_info(seller_id):
    user_input = input("품목 정보 수정을 원하시면 1번, 원하지 않고 메인 페이지로 돌아가기를 원하시면 나머지 버튼을 눌러주세요 : ")
    if user_input == '1':
        print("내가 등록한 품목을 불러옵니다.")
        cursor = user_con.cursor()

        select_query=f"select * from product_view WHERE product_seller='{seller_id}';"
        cursor.execute(select_query)
        my_product_info = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(my_product_info, columns=columns)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

        try :
            seller_input = input("제품 상위 코드 수정을 원하시면 1번, 바로 하위 제품을 수정하고 싶으시면 다른 버튼을 눌러주세요 : ").strip()
            if seller_input != "1":
                print("하위 제품 수정 페이지로 이동합니다!")
            else:
                print("상위 제품군 수정을 시작합니다.")
                topcode = int(input("수정하고 싶은 상위 제품군 코드번호를 입력해주세요 : ").strip())
                print(f"수정을 원하는 상위 제품군 코드번호는 {topcode}입니다.")

                print("수정 시작합니다.")

                top_category = input("상위 카테고리 : ").strip()
                sub_category = input("하위 카테고리 : ").strip()
                product_name = input("상품 이름 : ").strip()
                product_explain = input("상품 설면 : ").strip()

                update_query = f"UPDATE top_product SET top_category='{top_category}' , sub_category ='{sub_category}', product_name='{product_name}', product_explain='{product_explain}' WHERE topcode={topcode};"
                cursor.execute(update_query)
                user_con.commit()
                print("상위 제품군 수정을 완료하였습니다!")

                want_fix_sub_product_flag = input("하위 제품 수정을 원하시면 1번을 눌러주세요 : ")

                if want_fix_sub_product_flag != '1':
                    print("수정을 완료했습니다. 메인 페이지로 돌아갑니다.")
                    return

            print("하위 제품 수정을 시작합니다!")
            print("내가 등록한 하위 제품을 불러옵니다.")

            fix_want_sub_product = input("수정하고 싶은 하위 제품 코드를 입력해주세요 : ")
            print(f"수정을 원하는 하위 제품 코드번호는 {fix_want_sub_product}입니다.")

            print("수정 시작합니다.")

            size = input("사이즈 (S,M,L,XL)중 입력하세요: ").strip()
            color = input("색상 : ").strip()
            price = int(input("가격 : ").strip())
            amount = int(input("재고량 : ").strip())

            print("수정 시작합니다..")
            update_query = f"UPDATE sub_product SET product_size='{size}', product_color='{color}', product_price={price}, product_count={amount} WHERE subcode={fix_want_sub_product}"
            cursor.execute(update_query)
            user_con.commit()
            print("하위 제품 수정 완료됐습니다!")
            print("메인으로 돌아갑니다.")
        except Exception as e:
            print(f"에러 발생 : {e}, 양식에 맞추어 입력해주세요.")
            print("메인으로 돌아갑니다.")
            return

# 품목 조회 및 집계
# 판매등록 코드, 제품군
# 판매했던 정보 -> 누적 금액
def check_my_product(seller_id):
    user_input = input("내가 등록했던 품목 정보 열람을 원하시면 1번, 원하지 않고 메인 페이지로 돌아가기를 원하시면 1을 제외한 버튼을 눌러주세요 : ")
    cursor = user_con.cursor()
    print("정보 조회를 시작합니다")
    print("판매했던 정보를 불러옵니다 ...")
    select_query = f"select * FROM order_review_table WHERE seller_id ='{seller_id}';"
    cursor.execute(select_query)
    my_sell_product = cursor.fetchall()
    print("주문번호, 판매자 이름, 재고번호, 수량, 1개당 가격, 구매한 사람 , 고객 결제 날짜, 리뷰 포인트, 사용자 키, 사용자 몸무게 순으로 보여집니다.")
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame(my_sell_product, columns=columns)
    print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))


    print("총 판매 금액 집계중입니다 ... ")
    select_query = f"select seller_id, sum(count*price_per_1) FROM order_review_table WHERE seller_id='{seller_id}' GROUP BY seller_id; "
    cursor.execute(select_query)
    my_aggregation = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame(my_aggregation, columns=columns)
    print("총 판매 금액")
    print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
    print("메인 페이지로 돌아갑니다.")


def qna_answer(seller_id):
    print("QnA 게시판입니다.")
    cursor = user_con.cursor()
    try :
        print("내가 등록한 품목을 불러옵니다.")
        select_query = f"select * from product_view WHERE product_seller='{seller_id}';"
        cursor.execute(select_query)
        my_product_info = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(my_product_info, columns=columns)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

        print("QnA 게시판 불러옵니다..")
        select_query= f"select * FROM qna WHERE seller_id='{seller_id}';"
        cursor.execute(select_query)
        qna_list= cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(qna_list, columns=columns)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

        qna_num = int(input("답변하고 싶은 QnA num을 입력해주세요 : ").strip())
        answer = input("답변하고 싶은 대답을 입력해주세요 : ").strip()

        update_query =f"UPDATE qna SET answer='{answer}' WHERE qna_num ={qna_num};"
        cursor.execute(update_query)
        user_con.commit()
        print("답변 달았습니다. ")
        mail = input("메일 보내시기 원하시면 1번, 아니면 2번을 눌러주세요 : ").strip()
        if mail=='1':
            send_mail()

    except Exception as e:
        print(f"{e}: 입력 양식을 맞춰주세요")
    print("메인 페이지로 이동합니다.")

def send_mail():
    title = input("메일 제목을 입력하세요 : ")
    content = input("메일 내용을 입력하세요 : ")

    msg = MIMEText(content)
    msg['Subject'] = title
    print("구글 계정으로 메일을 보냅니다. 구글 계정과 Gmail 앱 비밀번호가 없으시다면 가입 후 사용해주시길 바랍니다.")
    print("Gmail 앱 비밀번호를 발급받는 방법 1단계 : Gmail 홈에서 톱니바퀴 > 빠른 설정 > 모든 설정 보기")
    print("Gmail 앱 비밀번호를 발급받는 방법 2단계 : IMAP 사용하기 설정")
    print("Gmail 앱 비밀번호를 발급받는 방법 3단계 : Google 계정 관리 > 보안 > 2단계 인증")
    print("Gmail 앱 비밀번호를 발급받는 방법 4단계 : 인증 완료 후 OTP 추가")
    print("Gmail 앱 비밀번호를 발급받는 방법 5단계 : 2단계 인증 시작화면으로 들어와서, 앱 비밀번호 설정.")
    print("Gmail 앱 비밀번호를 발급받는 방법 6단계 : 앱 비밀번호 생성 > 기타(맞춤 이름) ")
    print("16자리 우측 상단 기기용 앱 비밀번호를 기억해주세요.")

    # (*)메일의 발신자 메일 주소, 수신자 메일 주소, 앱비밀번호(발신자)
    sender = 'amm012450@gmail.com'
    receiver = 'amm0124@naver.com'
    app_password = 'okwradwukzflidiq'

    #sender = input("보내는 사람의 구글 계정을 입력해주세요.")
    #receiver = input("받는 사람의 구글 계정을 입력해주세요.")
    #app_password = input("16자리 앱 비밀번호를 입력해주세요 : ")

    with smtplib.SMTP('smtp.gmail.com', 587) as s:  # TLS 암호화
        s.starttls()
        s.login(sender, app_password)
        s.sendmail(sender, receiver, msg.as_string())
    print("메일 발송이 완료되었습니다.")


def print_administor_main_page():
    print("--------관리자 메인 페이지입니다!---------")
    print("1번을 누르면 판매 집계 정보를 열람할 수 있습니다.")
    print("2번을 누르면 당첨자 메일 발송을 할 수 있습니다.")
    print("3번을 누르면 개인 정보를 수정할 수 있습니다.")
    print("그 외를 누르면 프로그램을 종료합니다.")

def administor_main(administor_id):
    global user_con

    user_con = psycopg2.connect(
        database='termproject',
        user='administor',
        password='administor1',
        host='::1',
        port='5432'
    )

    print(f"안녕하세요. {administor_id} 관리자님")
    print_administor_main_page()

    type= input("입력 : ").strip()
    if type=="1":
        aggregation_product(administor_id)
    elif type=='2' :
        candidate_send_mail(administor_id)
    elif type=='3' :
        fix_my_account(administor_id, '3')
    else :
        print("프로그램 종료")
        sys.exit()
    administor_main(administor_id)
def candidate_send_mail(administor_id):
    global user_con
    cursor = user_con.cursor()
    print("이벤트 참여자에게 메일을 보냅니다!")
    try :
        current_time = datetime.now(timezone.utc)
        yesterday = current_time - timedelta(days=1)
        print("어제 참여 후 24시간 지난 사람들 목록입니다.")
        select_query = f"SELECT event_candidate_customer_id FROM event_table WHERE participation_start_time < '{yesterday.isoformat()}'"
        cursor.execute(select_query)
        candidate_list = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(candidate_list, columns=columns)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

        print("어제 참여자 중 랜덤하게 한 명 뽑았습니다 . .")
        select_query = f"SELECT event_candidate_customer_id FROM event_table WHERE participation_start_time < '{yesterday.isoformat()}' ORDER BY RANDOM() LIMIT 1"
        cursor.execute(select_query)
        selected_candidate = cursor.fetchone()[0]
        print(f"선택된 이벤트 참여자 아이디: {selected_candidate}")

        title = input("메일 제목을 입력하세요 : ")
        content = input("메일 내용을 입력하세요 : ")
    
        msg = MIMEText(content)
        msg['Subject'] = title
        print("구글 계정으로 메일을 보냅니다. 구글 계정과 Gmail 앱 비밀번호가 없으시다면 가입 후 사용해주시길 바랍니다.")
        print("Gmail 앱 비밀번호를 발급받는 방법 1단계 : Gmail 홈에서 톱니바퀴 > 빠른 설정 > 모든 설정 보기")
        print("Gmail 앱 비밀번호를 발급받는 방법 2단계 : IMAP 사용하기 설정")
        print("Gmail 앱 비밀번호를 발급받는 방법 3단계 : Google 계정 관리 > 보안 > 2단계 인증")
        print("Gmail 앱 비밀번호를 발급받는 방법 4단계 : 인증 완료 후 OTP 추가")
        print("Gmail 앱 비밀번호를 발급받는 방법 5단계 : 2단계 인증 시작화면으로 들어와서, 앱 비밀번호 설정.")
        print("Gmail 앱 비밀번호를 발급받는 방법 6단계 : 앱 비밀번호 생성 > 기타(맞춤 이름) ")
        print("16자리 우측 상단 기기용 앱 비밀번호를 기억해주세요.")
    
        # (*)메일의 발신자 메일 주소, 수신자 메일 주소, 앱비밀번호(발신자)
        sender = 'amm012450@gmail.com'
        #receiver = candidate_list[0][0]
        receiver = selected_candidate
        app_password = 'okwradwukzflidiq'
    
        sender = input("보내는 사람의 구글 계정을 입력해주세요.")
        # receiver = input("받는 사람의 구글 계정을 입력해주세요.")
        app_password = input("16자리 앱 비밀번호를 입력해주세요 : ")
    
        with smtplib.SMTP('smtp.gmail.com', 587) as s:  # TLS 암호화
            s.starttls()
            s.login(sender, app_password)
            s.sendmail(sender, receiver, msg.as_string())
        print("메일 발송이 완료되었습니다.")

        delete_query = f"DELETE FROM event_table WHERE participation_start_time < '{yesterday.isoformat()}'"
        cursor.execute(delete_query)
        user_con.commit()
        print("24시간 지난 참여한 사람들의 데이터가 삭제되었습니다.")


    except Exception as e :
        print(f"에러가 발생했습니다 : {e}")
        print("메인 페이지로 돌아갑니다")

def aggregation_product(administor_id):
    global user_con
    print("총 품목 집계를 시작합니다 . .")
    cursor = user_con.cursor()
    print("정보 조회를 시작합니다")
    print("판매했던 정보를 불러옵니다 ...")
    select_query = f"select * FROM order_review_table;"
    cursor.execute(select_query)
    my_sell_product = cursor.fetchall()
    print("주문번호, 판매자 이름, 재고번호, 수량, 1개당 가격, 구매한 사람 , 고객 결제 날짜, 리뷰 포인트, 사용자 키, 사용자 몸무게 순으로 보여집니다.")
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame(my_sell_product, columns=columns)
    print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

    print("총 판매 금액 집계중입니다 ... ")
    select_query = f"select seller_id, sum(count*price_per_1) FROM order_review_table GROUP BY seller_id; "
    cursor.execute(select_query)
    my_aggregation = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame(my_aggregation, columns=columns)
    print("총 판매 금액")
    print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
    print("메인 페이지로 돌아갑니다.")

if __name__ == '__main__':
    welcome()


