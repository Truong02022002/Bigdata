dir1 = {}
dir2 = {}

def xeploai_hocsinh(f1):
    with open(f1, "r") as f:
        for i in f:
            break
        for i in f:
            list = []
            i = i.strip().split(";")
            for j in range(1, len(i), 1):
                list.append(i[j].strip())
                dir1.update({i[0] : xl_theo_dtbinh(list)})
    print(dir1)

def xl_theo_dtbinh(temp):
    temp[0].strip()
    sum = 0
    for i in range(0, len(temp), 1):
        if i == 0 | i == 4 | i == 5:
            sum += float(temp[i]) * 2
        else:
            sum += float(temp[i])
        avg = sum / 11.0
    return xeploai(avg, temp)

def xeploai(avg, lst):
    if avg >= 9.0:
        if True != kiemtra(1, lst):
            return "Xuat sac"
    if avg >= 8.0:
        if True != kiemtra(2, lst):
            return "Gioi"
    if avg >= 6.5:
        if True != kiemtra(3, lst):
            return "Kha"
    if avg >= 6.0:
        if True != kiemtra(4, lst):
            return "TB kha"
    else:
        return "TB"


def kiemtra(check, lst):
    for i in lst:
        if (check == 1) & (float(i) < 8.0):
            return True
        if (check == 2) & (float(i) < 6.5):
            return True
        if (check == 3) & (float(i) < 5.0):
            return True
        if (check == 4) & (float(i) < 4.5):
            return True


def xeploai_thidaihoc_hocsinh(f1):
    with open(f1, "r") as f:
        for i in f:
            break
        for i in f:
            list = []
            i = i.strip().split(";")
            for j in range(1, len(i), 1):
                list.append(i[j].strip())
            dir2.update({i[0]: xeploai_khoi(list)})
        print(dir2)

def tinh_tong(*agr):
    tong = 0
    for i in agr:
        tong += float(i)
    return tong


def xeploai_khoi(temp):
    list = []
    list.append(sosanh_loai(tinh_tong(temp[0],temp[1],temp[2]),1))
    list.append(sosanh_loai(tinh_tong(temp[0],temp[1],temp[5]),1))
    list.append(sosanh_loai(tinh_tong(temp[0],temp[2],temp[3]),1))
    list.append(sosanh_loai(tinh_tong(temp[4],temp[6],temp[7]),2))
    list.append(sosanh_loai(tinh_tong(temp[0],temp[4],float(temp[5]) * 2),3))
    return list


def sosanh_loai(temp, check):
    if check == 1:
        if temp >= 24:
            return 1
        elif temp >= 18:
            return 2
        elif temp >= 12:
            return 3
        else:
            return 4
    if check == 2:
        if temp >= 21:
            return 1
        elif temp >= 15:
            return 2
        elif temp >= 12:
            return 3
        else:
            return 4
    if check == 3:
        if temp >= 32:
            return 1
        elif temp >= 24:
            return 2
        elif temp >= 20:
            return 3
        else:
            return 4


def luudiem_trungbinh(f2):
    try:
        with open(f2, "w") as f:
            	f.write("Ma HS, xeploai_TB chuan, xeploai_A, xeploai_A1, xeploai_B , xeploai_C, xeploai_D\n")
            	for i in dir1.keys():
		        f.write(i + "; ")
                f.write(dir1.get(i))
                for t in dir2.get(i):
                    f.write("; " + str(t))
                f.write("\n")
        print("Lưu file thành công!")
    except:
        print("Có lỗi!")


def main():
    #diem_trungbinh.txt
    file_1 = input("Nhập tập tin muốn xếp loại: ")
    xeploai_hocsinh(file_1)
    xeploai_thidaihoc_hocsinh(file_1)
    file_2 = input("Nhập tập tin muốn xếp loại: ")
    luudiem_trungbinh(file_2)

main()