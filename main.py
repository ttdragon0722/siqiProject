from flask import Flask,render_template,request,session,redirect
from flask_session import Session
from csv import reader
from json import dumps
from os import urandom
from io import BytesIO,TextIOWrapper
import secrets


app = Flask(__name__,template_folder="templates")
app.config['UPLOAD_FOLDER'] = 'uploads'  # 上传文件保存的目录
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv'}  # 允许上传的文件类型

app.config["SECRET_KEY"] = urandom(24)
app.secret_key = urandom(24)  # 16字節的隨機秘密金鑰
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

Session(app)


from ast import literal_eval

def list_to_string(my_list):
    """
    Convert a list of tuples to a string representation.
    """
    return ', '.join('({}, {}, {})'.format(*item) for item in my_list)

def string_to_list(result_string):
    """
    Convert a string representation back to a list of tuples.
    """
    return literal_eval(f'[{result_string}]')


def allowed_file(filename):
    # 检查文件扩展名是否在允许的扩展名集合中
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class Data():
    def __init__(self) -> None:
        self.data = []
    
    def getLimit(self):
        """
        生成資料邊界
        ---
        `Data.max` -> 最大邊界
        `Data.min` -> 最小邊界
        """
        maxNumber = abs(max(self.data))
        minNumber = abs(min(self.data))
        if maxNumber > minNumber:
            radius = maxNumber
        else:
            radius = minNumber
        minus = radius * 0.95
        self.max = minus
        self.min = minus*-1
        return (minus,minus*-1)

    def append(self,number:float) -> bool:
        self.data.append(number)
        return True
    
    def __max__(self):
        return max(self.data)
    
    def __min__(self):
        return min(self.data)
    
    def __len__(self):
        return len(self.data)

    def __iter__(self)->list:
        return iter(self.data)

class DataSet():
    def __init__(self,a,b) -> None:
        self.a = a
        self.b = b
        self.getColor()
        self.getRate()

    def getColor(self):
        self.good = [] 
        self.bad = []
        for a,b in zip(self.a,self.b):
            if a > self.a.max or a < self.a.min or b > self.b.max or b < self.b.min :
                self.bad.append({"x":a,"y":b})
            else :
                self.good.append({"x":a,"y":b})

    def getRate(self):
        self.rate = round(len(self.bad)/len(self.a)*100,2)

class DataModule:
    def setData(self):
        self.x = Data()
        self.y = Data()
        self.z = Data()
    
    def setLimit(self):
        self.x.getLimit()
        self.y.getLimit()
        self.z.getLimit()

    def setDataSet(self):
        self.len = len(self.x)
        self.xy = DataSet(self.x,self.y)
        self.xz = DataSet(self.x,self.z)
        self.yz = DataSet(self.y,self.z)

class DataReader(DataModule):
    def __init__(self,path) -> None:
        self.setData()

        with open(path,newline="") as csvfile:
            rows = reader(csvfile)
            rows.__next__()
            for row in rows:
                self.x.append(float(row[2]))
                self.y.append(float(row[3]))
                self.z.append(float(row[4]))
        
        self.setLimit()
        self.setDataSet()

        self.name = path.split("/")[-1].split(".")[0].split("\\")[-1]


class FileReader(DataModule):
    def __init__(self,data,name) -> None:
        self.setData()

        for v in data:
            self.x.append(float(v[0]))
            self.y.append(float(v[1]))
            self.z.append(float(v[2]))
        
        self.setLimit()
        self.setDataSet()

        self.name = name.split("/")[-1].split(".")[0].split("\\")[-1]

@app.route('/')
def index():
    return render_template("index.html")

# demo
@app.route("/demo")
def demo():
    return render_template("demo.html")
@app.route("/api/getDataset",methods=["GET"])
def getDataset():
    dataset = DataReader("upload/IXH6050HTXS-02下-20231009152611_COM4_1__RAW copy.csv")
    output = {
        "filename":dataset.name,
        "totalPoint":dataset.len,
        "xMin":min(dataset.x),
        "xMax":max(dataset.x),
        "yMin":min(dataset.y),
        "yMax":max(dataset.y),
        "zMin":min(dataset.z),
        "zMax":max(dataset.z),
        "xyGood":dataset.xy.good,
        "xyBad":dataset.xy.bad,
        "xyRate":dataset.xy.rate,
        "xzGood":dataset.xz.good,
        "xzBad":dataset.xz.bad,
        "xzRate":dataset.xz.rate,
        "yzGood":dataset.yz.good,
        "yzBad":dataset.yz.bad,
        "yzRate":dataset.yz.rate
    }
    return dumps(output)

@app.route("/readFile",methods=["POST"])
def readFile():
    file = request.files['file']

    if file:
        file.seek(0)
        file_name = file.filename
        file_content = str(file.read(),encoding="utf-8")
        data = []
        for row in file_content.split("\n")[1:-1]:
            row = row.split(",")[2:5]
            data.append(tuple(row))
        # session["file_name"] = file_name
        # session["file_content"] = list_to_string(data)

        # Save the file to a temporary location (optional)d
        # location = "./upload/"+file.filename
        # file.save(location)
        # # Read the CSV file using pandas
        # with open(location,newline="") as csvfile:
        #     f = reader(csvfile)
        #     for row in f:
        #         print(row)

        dataset = FileReader(file_name,data)
        output = {
            "filename":dataset.name,
            "totalPoint":dataset.len,
            "xMin":min(dataset.x),
            "xMax":max(dataset.x),
            "yMin":min(dataset.y),
            "yMax":max(dataset.y),
            "zMin":min(dataset.z),
            "zMax":max(dataset.z),
            "xyGood":dataset.xy.good,
            "xyBad":dataset.xy.bad,
            "xyRate":dataset.xy.rate,
            "xzGood":dataset.xz.good,
            "xzBad":dataset.xz.bad,
            "xzRate":dataset.xz.rate,
            "yzGood":dataset.yz.good,
            "yzBad":dataset.yz.bad,
            "yzRate":dataset.yz.rate
        }

        return dumps(output)
    else:
        return "no file"

@app.route("/show")
def show():
    print(session["file_name"])
    print(string_to_list(session["file_content"]))
    dataset = FileReader(session["file_name"],string_to_list(session["file_content"]))
    output = {
        "filename":dataset.name,
        "totalPoint":dataset.len,
        "xMin":min(dataset.x),
        "xMax":max(dataset.x),
        "yMin":min(dataset.y),
        "yMax":max(dataset.y),
        "zMin":min(dataset.z),
        "zMax":max(dataset.z),
        "xyGood":dataset.xy.good,
        "xyBad":dataset.xy.bad,
        "xyRate":dataset.xy.rate,
        "xzGood":dataset.xz.good,
        "xzBad":dataset.xz.bad,
        "xzRate":dataset.xz.rate,
        "yzGood":dataset.yz.good,
        "yzBad":dataset.yz.bad,
        "yzRate":dataset.yz.rate
    }
    return render_template("show.html",data=output)

if __name__ == "__main__":
    app.run()