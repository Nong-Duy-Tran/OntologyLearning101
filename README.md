# Ontology Learning
Sự bùng nổ của thông tin trong thời đại kỹ thuật số đã tạo ra nhu cầu cấp thiết về
việc biểu diễn và xử lý tri thức một cách hiệu quả và hiệu quả. Bản thể học (ontology),
với tư cách là các biểu diễn chính thức của các khái niệm hóa được chia sẻ trong một
miền, đã nổi lên như một công cụ mạnh mẽ cho việc tổ chức và lý luận tri thức. Tuy nhiên,
việc xây dựng và duy trì các ontology theo cách thủ công có thể là một quá trình tốn kém
và tốn thời gian, đặc biệt đối với các miền lớn và phức tạp.

Ontology learning giải quyết thách thức này bằng cách tự động hóa hoặc bán tự
động hóa quá trình thu thập ontology. Bằng cách tận dụng các kỹ thuật khác nhau như xử
lý ngôn ngữ tự nhiên, học máy và phân tích thống kê, học bản thể học nhằm mục đích
trích xuất kiến thức từ các nguồn dữ liệu đa dạng, bao gồm tài liệu văn bản, trang web và
cơ sở dữ liệu. Việc tự động hóa này mang lại nhiều lợi ích

## Brief Description
![model architecture](https://github.com/Nong-Duy-Tran/OntologyLearning101/blob/master/Pic/Ontology%20Model.png)

Mục tiêu của mô hình là trích xuất cấu trúc ba ngôi **(triplet)** tồn tại trong văn bản cho trước. Từ những triplet thu được từ trước đó, mô hình tiến hành
phân lớp các thực thể và các mối quan hệ sử dụng các công cụ như NER, Coref,... để tạo nên một cấu trúc phân cấp biểu thị ngữ nghĩa và các mối liên kết giữa các thực thể tồn tại trong văn bản

Kết quả của mô hình trả về một file ***.owl***, có thể sử dụng các công cụ bên thứ ba như ***protege*** để biểu diễn trực quan
