import chamber

class Entry :
    def __init__(self, data):
        self.data= data

    def csv(self):
        data = []
        for x in ('category', 'member_since', 'href',  'name'):
            if x in self.data:
                data.append(self.data[x])
            else:
                data.append("")

        if 'addr' in self.data:
            addr= self.data['addr']
            if addr:
                for x in addr:
                    for d in x :
                        v = x[d]
                        data.append(v)
            
        return data
import csv
with open('chamber.csv', 'wb') as csvfile:
    outfile = csv.writer(csvfile, delimiter=';',
                            quotechar='|')

    for x in chamber.data:
        outfile.writerow(Entry(x).csv())
