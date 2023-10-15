dir_cuoi = {}


def dtbinh (temp, sum=0):
    """Average score"""
    if len(temp) == 4:
        return float(temp[0]) * 0.05 + float(temp[1]) * 0.1 \
               + float(temp[2]) * 0.15 + float(temp[3]) * 0.7
    else:
        return float(temp[0]) * 0.05 + float(temp[1]) * 0.1 \
               + float(temp[2]) * 0.1 + float(temp[3]) * 0.15 + float(temp[4]) * 0.6


def tinhdiem_trungbinh(file_1):
    # asm2_data.txt
    f1 = open(file_1, "r")
    f1_lst = []
    mon_hoc = []

    for i in f1:
        i = i.strip()
        mon_hoc = i.split(',')
        break

    for i in f1:
        i = i.strip()
        f1_lst = i.split(";")
        dtb = {}
        for i2 in range(1, len(f1_lst), 1):
            if i2 == 1:
                f1_lst[1] = f1_lst[1].strip()
            f1_lst[i2] = f1_lst[i2].split(",")
            dtb.update({f"{mon_hoc[i2].strip()}": round(dtbinh(f1_lst[i2]),2)})
        dir_cuoi.update({f"{f1_lst[0]}": dtb})
    print(dir_cuoi)
    f1.close()


def luudiem_trungbinh(f1,f2):
    try:
        with open(f1, "r") as f_1:
            with open(f2, "w") as f_2:
                for i in f_1:
                    f_2.write(i)
                    break

                lst = dir_cuoi.keys()
                for j in lst:
                    f_2.write(j)
                    temp = dir_cuoi.get(j)
                    lst2 = temp.values()
                    for row in lst2:
                        if temp.get("Toan") == row:
                            f_2.write("; " + str(row))
                            continue
                        f_2.write(";" + str(row))
                    f_2.write("\n")
        print("Lưu file thành công")
    except:
        print("Có lỗi!")


def main():
    print("---------------------Tính toán điểm trung bình----------------------")
    # asm2_data.txt
    file1 = input("Mời nhập file cần tính điểm trung bình: ")
    tinhdiem_trungbinh(file1)
    file2 = input("Mời nhập tên để lưu file: ")
    luudiem_trungbinh(file1,file2)


main()
