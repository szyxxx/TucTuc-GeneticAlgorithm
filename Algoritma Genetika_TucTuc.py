import random
from tabulate import tabulate
import copy
import pandas as pd
import os

def hitung_jarak(jarak, kromosom):
    rincian_jarak = []
    total_jarak = 0

    for i in range(len(kromosom) - 1):
        gen_pair = kromosom[i:i + 2]
        total_jarak += jarak.get(gen_pair, 0)
        rincian_jarak.append(f"{jarak.get(gen_pair, 0)} ({gen_pair})")

    gen_pair_last = kromosom[-1] + kromosom[0]
    total_jarak += jarak.get(gen_pair_last, 0)
    rincian_jarak.append(f"{jarak.get(gen_pair_last, 0)} ({gen_pair_last})")

    rincian_str = " + ".join(rincian_jarak)
    return total_jarak, rincian_str

def update_data_populasi(data_populasi):
    updated_data_populasi = {}
    for key, data in data_populasi.items():
        kromosom_lengkap = 'A' + data['Lintasan'][1:-1].replace('A', '') + 'A'
        total_jarak, rincian_jarak = hitung_jarak(jarak, kromosom_lengkap)
        data.update({"Jarak": total_jarak, "Lintasan": kromosom_lengkap, "Rincian Jarak": rincian_jarak})
        updated_data_populasi[key] = {k: data[k] for k in ["Kromosom", "Lintasan", "Rincian Jarak", "Jarak"] + list(data.keys())[4:]}
    return updated_data_populasi

def inisialisasi_populasi():
    # populasi = [''.join(random.sample('BCDE', len('BCDE'))) for _ in range(6)]
    populasi = ['BDCE', 'CEBD', 'BEDC', 'DEBC', 'CBDE', 'ECDB']
    data_populasi = {}
    rata2 = 0
    inisialisasi_table = []

    for i, kromosom in enumerate(populasi, start=1):
        kromosom_lengkap = 'A' + kromosom + 'A'
        total_jarak, rincian_jarak = hitung_jarak(jarak, kromosom_lengkap)
        data_populasi[f"K{i}"] = {"Kromosom": f"K{i}", "Lintasan": kromosom_lengkap, "Rincian Jarak": rincian_jarak, "Jarak": total_jarak}
        rata2 += total_jarak
        inisialisasi_table.append([f"K{i}", kromosom_lengkap, rincian_jarak, total_jarak])

    print("="*120, f"\nStep 1 : Inisialisasi\n{tabulate(inisialisasi_table, headers=['Kromosom', 'Lintasan', 'Rincian Jarak', 'Jarak'], tablefmt='rounded_outline')}\nRata-rata = {rata2/len(inisialisasi_table):.3f}")
    
    return data_populasi

def evaluasi_kromosom(data_populasi):
    total_fitness = 0
    kromosom_list = list(data_populasi.values())
    evaluasi_table = []

    print("="*120)
    print("Step 2 : Evaluasi Kromosom")

    for data in kromosom_list:
        fitness = 1 / data['Jarak']
        print(f"Q[{data['Kromosom'][1:]}] = 1/{data['Jarak']} = {fitness}")
        total_fitness += fitness
        data['Fitness'] = fitness
        evaluasi_table.append([data['Kromosom'], data['Lintasan'], fitness])

    print("\nTabel Evaluasi Kromosom:")
    print(tabulate(evaluasi_table, headers=["Kromosom", "Lintasan", "Fitness"], tablefmt='rounded_outline'))
    print(f"Total Fitness {total_fitness}")
    return total_fitness, data_populasi

def fitness_relative(data_populasi, total_fitness):
    relative_table = []

    print(f"\na.) Fitness Relative")
    for i, data in enumerate(data_populasi.values(), start=1):
        hasil = data['Fitness'] / total_fitness
        print(f"P[{i}] = {data['Fitness']}/{total_fitness} = {hasil}")
        data['Fitness Relative'] = hasil
        relative_table.append([data['Kromosom'], data['Lintasan'], hasil])

    headers = ["Kromosom", "Lintasan", "Fitness Relative"]
    print(tabulate(relative_table, headers=headers, tablefmt="rounded_outline"))
    return relative_table, data_populasi

def fitness_cumulative(data_populasi):
    cumulative_table = []
 
    print(f"\nb.) Fitness Cumulative")
    total = 0

    for i, data in enumerate(data_populasi.values(), start=1):
        total += data['Fitness Relative']
        data['Fitness Cumulative'] = total
        operation = f"C[{i}] = {total:.6f}" if i == 1 else f"C[{i}] = C[{i - 1}] + {data['Fitness Relative']:.6f} = {total:.6f}"
        print(operation)
        range_str = f"> {total - data['Fitness Relative']:.6f} - {total:.6f}" if i > 1 else f"= 0.000000 - {total:.6f}"
        data['Range'] = range_str
        cumulative_table.append([data['Kromosom'], data['Lintasan'], data['Fitness Cumulative'], data['Range']])

    headers = ["Kromosom", "Lintasan", "Fitness Cumulative", "Range"]
    print(tabulate(cumulative_table, headers=headers, tablefmt="rounded_outline"))
    return data_populasi

def seleksi(data_populasi):
    print("="*120)
    print("Step 3 : Seleksi Kromosom")
    total_fitness, data_populasi = evaluasi_kromosom(data_populasi)
    relative_table, data_populasi = fitness_relative(data_populasi, total_fitness)
    data_populasi = fitness_cumulative(data_populasi)
    # R_Baru = [round(random.uniform(0,1),6) for _ in range(len(data_populasi.keys()))]
    R_Baru = [0.122,0.416,0.406,0.649,0.632,0.220]
    print("\nc.) Seleksi berdasarkan Roulette Wheel")
    for i, r_value in enumerate(R_Baru, start=1):
        print(f"R[{i}] = {r_value}")
    selected_indices = [f"K{i + 1}" for i, data in enumerate(data_populasi.values()) if R_Baru[i] <= data['Fitness Cumulative']]
    print(f"Kromosom yang terpilih berdasarkan Roulette Wheel: {selected_indices}")

    for i in data_populasi.keys():
        if i not in selected_indices:
            range_tukar = R_Baru[int(i[1]) - 1]
            kromosom_tukar = next((value for value in data_populasi.values() if value['Fitness Cumulative'] >= range_tukar), None)

            if kromosom_tukar:
                kromosom_tukar_attributes = ['Lintasan', 'Rincian Jarak', 'Jarak', 'Fitness', 'Fitness Relative', 'Fitness Cumulative']
                for attr in kromosom_tukar_attributes:
                    data_populasi[kromosom_tukar['Kromosom']][attr], data_populasi[i][attr] = (
                        data_populasi[i][attr], data_populasi[kromosom_tukar['Kromosom']][attr])

                print(f"Tukar Kromosom {i} dengan Kromosom {kromosom_tukar['Kromosom']}")
            else:
                print(f"Tidak ada kromosom yang dapat ditukar untuk Kromosom {i}")

    headers = ["Kromosom", "Lintasan", "Rincian Jarak", "Jarak", "Fitness", "Fitness Relative","Fitness Cumulative", "Range"]
    print("\nHasil setelah Seleksi:")
    print(tabulate([list(data.values()) for data in data_populasi.values()], headers=headers, tablefmt='rounded_outline'))
    return data_populasi

def crossover(data_populasi):
    print("=" * 120)
    print("Step 4 : Crossover")
    N = 2
    pasangan = [["K1", "K3", 0.48], ["K2", "K4", 0.507], ["K5", "K6", 0.113]]
    # pasangan = [["K" + str(i), "K" + str(random.randint(i+1, 6)), round(random.uniform(0, 1), 3)] for i in range(1, 6, 2)]
    # gen_tukar = sorted(random.sample(["B","C","D","E"],N))
    gen_tukar = ['B','E']
    pc = int(input("\nMasukkan Nilai Probabilitas Crossover (%): ")) / 100
    print(f"N = {N} ({gen_tukar})")
        
    for pasangan_kromosom in pasangan:
        if pasangan_kromosom[2] < pc:
            kromosom_1, kromosom_2, r_value = pasangan_kromosom

            print(f"\nCrossover antara {kromosom_1} dan {kromosom_2} dengan R = {r_value}")

            print(f"Before Crossover:")
            print(f"{kromosom_1} = {data_populasi[kromosom_1]['Lintasan']}")
            print(f"{kromosom_2} = {data_populasi[kromosom_2]['Lintasan']}")

            offspring_1 = list(data_populasi[kromosom_1]['Lintasan'])
            offspring_2 = list(data_populasi[kromosom_2]['Lintasan'])

            for i in range(len(offspring_1)):
                if offspring_1[i] in gen_tukar:
                    replacement_gene = random.choice([gen for gen in gen_tukar if gen != offspring_1[i]])
                    offspring_1[i] = replacement_gene

            for i in range(len(offspring_2)):
                if offspring_2[i] in gen_tukar:
                    replacement_gene = random.choice([gen for gen in gen_tukar if gen != offspring_2[i]])
                    offspring_2[i] = replacement_gene

            offspring_1_str = ''.join(offspring_1)
            offspring_2_str = ''.join(offspring_2)

            data_populasi[kromosom_1]['Lintasan'] = offspring_1_str
            data_populasi[kromosom_2]['Lintasan'] = offspring_2_str

            print(f"After Crossover:")
            print(f"{kromosom_1} = {data_populasi[kromosom_1]['Lintasan']}")
            print(f"{kromosom_2} = {data_populasi[kromosom_2]['Lintasan']}")

    data_populasi = update_data_populasi(data_populasi)

    print(f"Kromosom Hasil Crossover:")
    print(tabulate([[data['Kromosom'], data['Lintasan'], data['Rincian Jarak'], data['Jarak']] for data in data_populasi.values()], headers=["Kromosom", "Lintasan", "Rincian Jarak", "Jarak"], tablefmt='rounded_outline'))
    return data_populasi

def mutasi(data_populasi):
    print("=" * 120)
    print("Step 5 : Mutasi")
    N = 2
    # R = [0.765, 0.623, 0.804, 0.430, 0.571, 0.398]
    R = [round(random.uniform(0,1),6) for _ in range(len(data_populasi.keys()))]
    gen_tukar = sorted(random.sample(["B","C","D","E"],N))
    # gen_tukar = ['B','C']
    pm = int(input("\nMasukkan Nilai Probabilitas Mutasi (%): ")) / 100
    print(f"N = {N} ({gen_tukar})")


    for i, r_value in enumerate(R, start=1):
        print(f"\nMutasi untuk Kromosom K{i} dengan R = {r_value}")


        print(f"Sebelum Mutasi:")
        kromosom = f"K{i}"
        print(f"{kromosom} = {data_populasi[kromosom]['Lintasan']}")

        if r_value <= pm:
            print(f"Mutasi terjadi pada {kromosom}")

            offspring = list(data_populasi[kromosom]['Lintasan'])

            for j in range(len(offspring)):
                if offspring[j] in gen_tukar:
                    replacement_gene = random.choice([gen for gen in gen_tukar if gen != offspring[j]])
                    offspring[j] = replacement_gene

            offspring_str = ''.join(offspring)

            data_populasi[kromosom]['Lintasan'] = offspring_str

            print(f"Setelah Mutasi:")
            print(f"{kromosom} = {data_populasi[kromosom]['Lintasan']}")
        else:
            print(f"Mutasi tidak diperlukan pada {kromosom}")

    data_populasi = update_data_populasi(data_populasi)

    print("\nHasil setelah Mutasi:")
    print(tabulate([[data['Kromosom'], data['Lintasan'], data['Rincian Jarak'], data['Jarak']] for data in data_populasi.values()], headers=["Kromosom", "Lintasan", "Rincian Jarak", "Jarak"], tablefmt='rounded_outline'))

    return data_populasi

def elitism(data_populasi, data_populasi2):
    print("=" * 120)
    print("Step 6 : Elitism")

    print("Populasi Awal ")
    headers = ["Kromosom", "Lintasan", "Jarak"]
    print(tabulate([[data['Kromosom'], data['Lintasan'], data['Jarak']] for data in data_populasi2.values()], headers=headers, tablefmt='rounded_outline'))
    print("Rata-rata =",sum(data['Jarak'] for data in data_populasi2.values())/(len(data_populasi2)))

    max_distance_kromosom = max(data_populasi, key=lambda k: data_populasi[k]['Jarak'])

    min_distance_kromosom = min(data_populasi2, key=lambda k: data_populasi2[k]['Jarak'])

    data_populasi[max_distance_kromosom]['Lintasan'] = data_populasi2[min_distance_kromosom]['Lintasan']
    data_populasi[max_distance_kromosom]['Jarak'] = data_populasi2[min_distance_kromosom]['Jarak']

    print(f"\nGanti Lintasan dan Jarak {max_distance_kromosom} dengan {min_distance_kromosom} pada populasi awal")

    headers = ["Kromosom", "Lintasan", "Jarak"]
    print("\nHasil setelah Elitism:")
    print(tabulate([[data['Kromosom'], data['Lintasan'], data['Jarak']] for data in data_populasi.values()], headers=headers, tablefmt='rounded_outline'))
    print("Rata-rata =",sum(data['Jarak'] for data in data_populasi.values())/(len(data_populasi)))

if __name__ == "__main__":
    csv_file_path = "data_generasi.csv"
    generations_df = pd.DataFrame()

    jarak = {'AB': 300, 'AC': 500, 'AD': 850, 'AE': 450,
            'BA': 300, 'BC': 250, 'BD': 500, 'BE': 650,
            'CA': 500, 'CB': 250, 'CD': 350, 'CE': 400,
            'DA': 850, 'DB': 500, 'DC': 350, 'DE': 550,
            'EA': 450, 'EB': 650, 'EC': 400, 'ED': 550}

    
    data_populasi = inisialisasi_populasi()
    # os.system('cls' if os.name == 'nt' else 'clear')
    generasi = 0

    while True:
        populasi_terbaik = min(data_populasi.values(), key=lambda x: x['Jarak'])['Lintasan']
        rata2_generasi = sum(data['Jarak'] for data in data_populasi.values()) / len(data_populasi)
        generations_df = generations_df._append({"Generasi": generasi, "Rata-rata": rata2_generasi, "Populasi Terbaik": populasi_terbaik}, ignore_index=True)

        print(tabulate([[data['Kromosom'], data['Lintasan'], data['Rincian Jarak'], data['Jarak']] for data in data_populasi.values()], headers=["Kromosom", "Lintasan", "Rincian Jarak", "Jarak"], tablefmt='rounded_outline'))
        data_populasi2 = copy.deepcopy(data_populasi)
        total_fitness, data_populasi = evaluasi_kromosom(data_populasi)
        data_populasi = seleksi(data_populasi)
        data_populasi = crossover(data_populasi)
        data_populasi = mutasi(data_populasi)
        elitism(data_populasi, data_populasi2)
        generasi += 1

        if input("\nLanjut ke generasi berikutnya? (y/n): ") == 'y':
            if sum(data['Jarak'] for data in data_populasi.values()) > sum(data['Jarak'] for data in data_populasi2.values()) :
                rata2_generasi = sum(data['Jarak'] for data in data_populasi.values()) / len(data_populasi)
                generations_df = generations_df._append({"Generasi": generasi, "Rata-rata": rata2_generasi, "Populasi Terbaik": populasi_terbaik}, ignore_index=True)
                print("Generasi tidak dapat dilanjutkan. Generasi terhenti")
                break
    print("\nJumlah Generasi", generasi)
    generations_df.to_csv(csv_file_path, index=False)