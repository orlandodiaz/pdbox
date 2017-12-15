import requests
import pickle


def get_stocks():
    """

    :return:
    """
    RETRIES = 4
    stocks = []

    USER = '5125a193faf60ef5df93a9e0b0897d7b'
    PW = '82b9e088c62765383fa01df32f8abf36'
  #  url = "https://api.intrinio.com/securities/search?conditions=marketcap~lt~1000000000&page_size=500"
    url = 'https://api.intrinio.com/securities/search?conditions=marketcap~gt~250000000,marketcap~lt~10000000000&page_size=500'

    try:
        print "stock_screener: Getting request for stock screener",
        resp = requests.get(url, auth=(USER, PW), timeout=10)
        resp.raise_for_status()

    except requests.HTTPError as http_error:
        print "Server returned the following HTTP Error: {http_error}".format(http_error=http_error)

    except requests.exceptions.Timeout:
        print 'Timeout'

    else:
        print '\t SUCCESS'
        try:
            print "stock_screener: Trying to read json file . . .",

            data1 = resp.json()
            # print data1
        except Exception as ex:
            print ex
        else:
            #print data1
            if 'errors' in data1:
                print  data1['errors'][0]['human']
                raise ValueError(data1['errors'][0]['human'])

            else:
                print '\t SUCCESS\t',
                total_pages = data1['total_pages']
                result_count = data1['result_count']
                print "Total pages: {total_pages} \tresult_count: {result_count}"\
                        .format(total_pages=total_pages,result_count=result_count)

                stocks = []

                for p in range(1, total_pages+1):

                    url_new = url + "&page_number=" + str(p)

                    for r in range(RETRIES):
                        try:
                            print "stock_screener: \t Going to page number {p}".format(p=p),
                            resp = requests.get(url_new, auth=(USER, PW), timeout=10)

                            if resp.status_code == 503:
                                print 'stock_screener: 503 Error: Server is too busy. Retrying again'
                                resp.raise_for_status()

                        except Exception as ex:
                            print ex
                            continue
                        else:
                            print 'stock_screener: SUCCESS'
                            data = resp.json()
                            #print data
                            for stock in data['data']:
                                stocks.append(str(stock['ticker']))
                            break
            return stocks


if __name__ == '__main__':

    stocks  = get_stocks()
    pickle_name = "stocks_250_to_1b.p"
    print "Pickling object stocks as {pickle_name}".format(pickle_name=pickle_name)
    pickle.dump(stocks, open(pickle_name, "wb" ) )
    #pickle.dump(stocks, open( "stocks_less_than_200m.p", "wb" ) )

    # TODO: Historical stock screening data. You are currently biased and are usign future screening results from today
