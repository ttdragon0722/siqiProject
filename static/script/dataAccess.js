class Data {
    constructor() {
        this.data = []
    }
    
    /**
     * 添加值
     * @param {string} value 
     * @returns boolean
     */
    append(value) {
        value = parseFloat(value);
        if (typeof value === 'number' && !isNaN(value)) {
            this.data.push(value);
            return true;
        } else {
            return false;
        }
    }

    getLimit() {
        this.maximum = Math.max(...this.data);
        this.minimum = Math.min(...this.data);
        let maxNumber = Math.abs(this.maximum);
        let minNumber = Math.abs(this.minimum);
        let radius =(maxNumber > minNumber) ? maxNumber:minNumber;
        let minus = radius * 0.95;
        this.max = minus;
        this.min = minus*-1;
        return (this.max,this.min);
    }

    *[Symbol.iterator]() {
        for (const item of this.data) {
            yield item;
        }
    }

    get length() {
        return this.data.length;
    }
}
class DataSet{
    /**
     * @param {Data} a Data模組
     * @param {Data} b Data模組
     */
    constructor(a,b) {
        this.a = a;
        this.b = b;
        this.getColor();
        this.getRate();
    }

    *zip() {
        for(let i=0; i<this.a.length; i++){
            // todo del
            yield [this.a.data[i],this.b.data[i]];
        }
    }

    getColor() {
        this.good = [];
        this.bad = [];
        for (const [a,b] of this.zip()) {

            if (a > this.a.max || a < this.a.min || b > this.b.max  || b < this.b.min) {

                this.bad.push({"x":a,"y":b});
            } else {
    
                this.good.push({"x":a,"y":b});
            }
        }
    }

    getRate() {
        this.rate = ((this.bad.length / this.a.length)*100).toFixed(2);
    }
}

class DataModule {
    /**
     * 建立資料
     * @param {array} data 傳入建立的資料
     */
    setData(src) {
        this.x = new Data();
        this.y = new Data();
        this.z = new Data();

        for (const data of src) {
            this.x.append(data[2]);
            this.y.append(data[3]);
            this.z.append(data[4]);
        }
        this.len = this.x.length;
    }
    setLimit() {
        this.x.getLimit();
        this.y.getLimit();
        this.z.getLimit();
    }
    setDataSet() {
        this.xy = new DataSet(this.x,this.y);
        this.xz = new DataSet(this.x,this.z);
        this.yz = new DataSet(this.y,this.z);
    }
}

class DataReader extends DataModule {
    /**
     * 建立資料！
     * @param {array} data papaParse讀到的資料
     */
    constructor(filename,data) {
        super();
        this.filename = filename;
        this.setData(data);
        this.setLimit();
        this.setDataSet();
    }
}