# Diem_Danh_Bang_Khuon_Mat


# 1. Xây dựng mô hình nhận diện

Để nhận diện khuôn mặt trong bức ảnh, mình sử dụng InsightFace. InsightFace có 2 bước đó là detect và recognize.<br>
Bức ảnh sau khi được detect sẽ cho ta các landmarks, rồi từ các landmarks cho ra một embedding (, 512).<br>
Sau khi có các embeddings và classes tương ứng, ta chỉ cần dùng một classifier là có thể nhận diện được ai trong bức ảnh.<br>

Tại folder Face-Recognize, dữ liệu huấn luyện được đặt tại **datasetsz**, trong đó, mỗi folder là một bộ ảnh khuôn mặt của một người, trên folder là id của người đó.<br>
**valset** chứa dữ liệu kiểm tra, cũng có cấu trúc tương tự **datasetsz**.

     \---file_name
            +---id_class1
            |   img1.jpg
            |   img2.jpg
            |   ...
            +---id_class2
            |   img1.jpg
            |   img2.jpg
            |   ...
            ...
        
## Install environments
    pip install -r requirements.txt
    
## Quick start

### Chuẩn bị dữ liệu
     python ./prepare_dataset.py

Lúc này, chương trình sẽ xuất ra 2 files X.npy và y.npy tương ứng với features và targets tại thư mục model.

### Train
    python ./train.py
    
Minh sử dụng thuật toán KNN với số lân cận là 3.<br>
Chương trình sẽ huấn luyện X và y, rồi xuất ra 1 pretrained model có tên mặc định là my_model.sav.

### Validate
    python ./val.py
    
Chương trình sẽ sử dụng mô hình nhận diện mới huấn luyện xong, kiểm tra lại với tập kiểm tra.<br>
Kết quả sẽ là một file .csv, trong đó có *Global Confident Threshold*, và *Class Confident Threshold* của từng người.<br>
Trong quá trình triển khai, khi một người được nhận diện, nếu ngưỡng chắc chắn trên ngưỡng Global, thì sẽ tiếp tục kiểm tra với ngưỡng của riêng người đó (Class Confident Threshold). Ngược lại khi không đạt đủ ngưỡng thì sẽ cho ra kết quả là "Không xác định".

Kết quả này sẽ được đưa vào Cơ sở dữ liệu với tên bảng là **confident_table**, còn thông tin của từng người sẽ ở bảng **member**.

![image](https://user-images.githubusercontent.com/72682397/156749573-547b9891-728a-44ad-9034-be5493bf4a45.png)



# 2. Flask Server

Tại folder web app

    python flask_app.py
    
Tiến hành chọn 1 bức ảnh, rồi nhấn Predict, chúng ta sẽ được kết quả sau:
![image](https://user-images.githubusercontent.com/72682397/156750775-bc5c17a4-9ace-43e7-baf4-c98ad014ac1f.png)
Những người không có trong CSDL sẽ được gán là Unknown, còn ai có trong CSDL sẽ truy vấn ra thông tin của người đó.


<hr>
Đây mới chỉ là webapp sơ khai với tính năng cơ bản nhất để test mô hình.<br>
Trong tương lai, mình sẽ phát triển thêm các tính năng khác như:<br>

* Ghi nhận thời gian điểm danh

* Điểm danh theo danh sách lớp

* Điểm danh qua webcam
    
* ...
    
