from ids import *
import numpy as np
import matplotlib.pyplot as plt

__author__ = "ee595"


def import_data(file=None):
    with open(file) as f:
        lines = f.readlines()
    data = [float(x.strip()) for x in lines]
    return data


# TODO: Plot accumulated offset curves for both state-of-the-art and NTP-based IDSs.
def plot_acc_offsets(ids, mode):
    # ====================== Start of Your Code =========================
    if mode == 'state-of-the-art':
        suffix, title, fname = 'sota', 'State-of-the-Art IDS', 'SOTA'
    elif mode == 'ntp-based':
        suffix, title, fname = 'ntp', 'NTP-Based IDS', 'NTP'
    else:
        raise ValueError('Unknown IDS mode')

    N = ids['184-' + suffix].N
    plt.figure()
    for msg in ['184', '3d1', '180']:
        d = ids[msg + '-' + suffix]
        # The final RLS skew estimate is the slope of the curve (ppm = us/s)
        plt.plot(d.elapsed_time_sec_hist, d.acc_offset_us_hist,
                 label='0x%s (S = %.2f ppm)' % (msg, d.skew))
    plt.xlabel('Elapsed Time (s)')
    plt.ylabel(r'Accumulated Offset ($\mu$s)')
    plt.title('Accumulated Offset, %s, N = %d' % (title, N))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('../../plots/%s_offset_acc_%d.png' % (fname, N), dpi=150, bbox_inches='tight')
    plt.show()
    # ====================== End of Your Code =========================


# TODO: Implement this simulation (N=20)
def simulation_masquerade_attack(mode):
    if mode == 'state-of-the-art':
        # The following code is provided as an example.
        data_184 = import_data('../data/184.txt')
        data_3d1 = import_data('../data/3d1.txt')

        N = 20

        # Construct a new data-set with the first 1000 batches of data_184,
        # followed by 1000 batches of data_3d1. That is, the masquerade
        # attack occurs at the 1001-st batch.
        data_184 = np.asarray(data_184[0:1000 * N]) - data_184[0]  # Relative timestamps
        data_3d1 = np.asarray(data_3d1[0:1000 * N]) - data_3d1[0]  # Relative timestamps
        data = np.append(data_184, data_184[-1] + 0.1 + data_3d1)  # The 1st spoofed message occurs exactly 0.1 sec
                                                                   # (the period) after the last legitimate message.

        ids = IDS(T_sec=0.1, N=N, mode='state-of-the-art')

        batch_num = 2000
        for i in range(batch_num):
            batch = np.asarray(data[i * N:(i + 1) * N])
            ids.update(batch)

        plt.plot(ids.L_upper_hist, label='Upper Control Limit')
        plt.plot(ids.L_lower_hist, label='Lower Control Limit')
        plt.xlabel('Number of Batches')
        plt.ylabel('Control Limits')
        plt.title('Control Limits for State-of-the-Art IDS')
        plt.legend()
        plt.show()
    elif mode == 'ntp-based':
        # ====================== Start of Your Code =========================
        
        # Your code goes here.
        pass
        
        # ====================== End of Your Code  =========================


# TODO: Implement this simulation (N=20)
def simulation_cloaking_attack(mode):
    if mode == 'state-of-the-art':
        # ====================== Start of Your Code =========================
        
        # Your code goes here.
        pass

        # ====================== End of Your Code =========================

    elif mode == 'ntp-based':
        # ====================== Start of Your Code =========================
        
        # Your code goes here.
        pass

        # ====================== End of Your Code =========================


if __name__ == '__main__':
    # If IDS is correctly implemented, you should be able to run the following code.
    data_184 = import_data('../data/184.txt')
    data_3d1 = import_data('../data/3d1.txt')
    data_180 = import_data('../data/180.txt')

    data_184 = np.asarray(data_184) - data_184[0]
    data_3d1 = np.asarray(data_3d1) - data_3d1[0]
    data_180 = np.asarray(data_180) - data_180[0]

    # Tasks 2-4: run both IDSs on all three messages for N = 20 and N = 30.
    for N in [20, 30]:
        ids = dict()
        for msg in ['184', '3d1', '180']:
            ids[msg + '-sota'] = IDS(T_sec=0.1, N=N, mode='state-of-the-art')
            ids[msg + '-ntp'] = IDS(T_sec=0.1, N=N, mode='ntp-based')

        if N == 20:
            batch_num = 6000
        elif N == 30:
            batch_num = 4000
        else:
            batch_num = 6000

        data = {'184': data_184, '3d1': data_3d1, '180': data_180}
        for i in range(batch_num):
            for msg in ['184', '3d1', '180']:
                batch = data[msg][i * N:(i + 1) * N]
                ids[msg + '-sota'].update(batch)
                ids[msg + '-ntp'].update(batch)

        for msg in ['184', '3d1', '180']:
            print('N=%d  0x%s  skew: SOTA = %8.3f ppm, NTP = %8.3f ppm'
                  % (N, msg, ids[msg + '-sota'].skew, ids[msg + '-ntp'].skew))

        # Task 2 (N=20) / Task 4 (N=30): state-of-the-art IDS
        plot_acc_offsets(ids, "state-of-the-art")
        # Task 3 (N=20) / Task 4 (N=30): NTP-based IDS
        plot_acc_offsets(ids, "ntp-based")

    # Task 5: Simulate the masquerade attack, and plot upper/lower control limits.
    simulation_masquerade_attack("state-of-the-art")
    simulation_masquerade_attack("ntp-based")

    # Task 6: Simulate the cloaking attack, and plot upper/lower control limits.
    simulation_cloaking_attack("state-of-the-art")
    simulation_cloaking_attack("ntp-based")