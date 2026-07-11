import csv

skip_unit: int = (
    int(input('5분 단위의 가공 시간 단위를 입력하여 주세요. (e.g., 20분 -> 20): ')) // 5) - 1
DELETE_TOTAL_DEMAND_FEATURE: bool = True if input(
    'totalDemand 열을 삭제할까요? (y/n): ') == 'y' else False

new_csv_data: list[list[str]] = []
with open('../data/kpx/kpx_data.csv', 'r', encoding='utf8') as file:
    csv_reader = csv.reader(file)

    row: list[str] = next(csv_reader)  # 첫 줄은 무조건 넣기 (Header)
    if DELETE_TOTAL_DEMAND_FEATURE:
        del row[1]
    new_csv_data.append(row)
    for row in csv_reader:  # 더해서 해야하는데 무작정 자르기만 함.
        total: str = row[2]
        for _ in range(skip_unit):
            try:
                temp: list[str] = next(csv_reader)
                total += temp[2]
            except StopIteration:
                break
        if DELETE_TOTAL_DEMAND_FEATURE:
            del row[1]
        new_csv_data.append(row)

with open('./data/kpx/kpx_data_preprocessed.csv', 'w', encoding='utf8', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerows(new_csv_data)
