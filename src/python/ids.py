"""
This implements both state-of-the-art and NTP-based IDSs.
"""

import numpy as np

__author__ = "ee595"


class IDS:
    def __init__(self, T_sec, N, mode):
        if (mode != 'state-of-the-art') & (mode != 'ntp-based'):
            raise ValueError('Unknown IDS mode')

        self.mode = mode

        self.k = 0  # Current batch
        self.N = N  # Batch size
        self.T_sec = T_sec # Nominal period in sec

        self.mu_T_sec = 0            # Average inter-arrival time in the current batch (sec)
        self.batch_end_time_sec = 0  # End time of every batch (sec)
        self.init_time_sec = 0       # Arrival time of the 1st message in the 2nd batch (sec)
        self.elapsed_time_sec = 0    # Elapsed time since the 1st message in the 2nd batch (sec)

        self.acc_offset_us = 0  # Most recent accumulated offset (us)
        self.avg_offset_us = 0  # Most recent average offset (us)
        self.skew = 0           # Most recent estimated skew (ppm)
        self.P = 1              # Parameter used in RLS

        self.mu_T_sec_hist = []
        self.batch_end_time_sec_hist = []
        self.elapsed_time_sec_hist = []
        self.acc_offset_us_hist = []
        self.avg_offset_us_hist = []
        self.skew_hist = []
        self.error_hist = []

        # CUSUM
        self.is_detected = 0

        self.n_init = 50  # Number of error samples for initializing mu_e and sigma_e
        self.k_CUSUM_start = self.n_init + 1  # CUSUM starts after mu and sigma are initialized

        self.Gamma = 5  # Control limit threshold
        self.gamma = 4  # Update threshold
        self.kappa = 8  # Sensitivity parameter in CUSUM

        self.L_upper = 0  # Most recent upper control limit
        self.L_lower = 0  # Most recent upper control limit
        self.e_ref = []   # Reference (un-normalized) error samples; used to compute mu_e and sigma_e

        self.L_upper_hist = []
        self.L_lower_hist = []

    # `a` is a 1-by-N vector that contains arrival timestamps of the latest batch.
    def update(self, a):
        if len(a) != self.N:
            raise ValueError('Inconsistent batch size')

        self.k += 1
        self.batch_end_time_sec_hist.append(a[-1])

        if self.k == 1:     # Initialize something in the first batch
            if self.mode == 'state-of-the-art':
                self.mu_T_sec = np.mean(a[1:] - a[:-1])
            return

        # CIDS officially starts from the second batch
        if self.k == 2:
            self.init_time_sec = a[0]

        if self.k >= 2:
            curr_avg_offset_us, curr_acc_offset_us = self.estimate_offset(a)
            curr_error_sample = self.update_clock_skew(curr_avg_offset_us, curr_acc_offset_us)
            self.update_cusum(curr_error_sample)

    def estimate_offset(self, a):
        self.elapsed_time_sec = a[-1] - self.init_time_sec
        self.elapsed_time_sec_hist.append(self.elapsed_time_sec)

        prev_mu_T_sec = self.mu_T_sec           # You will use it later.
        self.mu_T_sec = np.mean(a[1:] - a[:-1])
        self.mu_T_sec_hist.append(self.mu_T_sec)

        prev_acc_offset_us = self.acc_offset_us # You will use it later.
        a0 = self.batch_end_time_sec_hist[-2]   # Arrival timestamp of the last message in the previous batch
                                                # You will use it later. 

        curr_avg_offset_us, curr_acc_offset_us = 0, 0

        if self.mode == 'state-of-the-art':
            # ====================== Start of Your Code =========================
            # TODO: Compute curr_avg_offset_us and curr_acc_offset_us for state-of-the-art IDS

            # Your code goes here. 
            cumsum=0
            for i in range(1,self.N):
                cumsum += a[i] - (a[0]+(i-1) * prev_mu_T_sec)
            curr_avg_offset_us = (cumsum/(self.N-1))/10**-6

            curr_acc_offset_us = prev_acc_offset_us + np.abs(curr_avg_offset_us)
            
            # ====================== End of Your Code =========================

        elif self.mode == 'ntp-based':
            # ====================== Start of Your Code =========================
            # TODO: Compute curr_avg_offset_us and curr_acc_offset_us for NTP-based IDS

            # Your code goes here. 

            curr_avg_offset_us = self.T_sec - ((a[self.N] - a0) / self.N)
            curr_acc_offset_us = prev_acc_offset_us + (self.N * curr_avg_offset_us)

            # ====================== End of Your Code =========================

        #udpate acc_offset and history
        self.acc_offset_us = curr_acc_offset_us
        self.acc_offset_us_hist.append(self.acc_offset_us)

        return curr_avg_offset_us, curr_acc_offset_us

    def update_clock_skew(self, curr_avg_offset_us, curr_acc_offset_us):
        prev_skew = self.skew
        prev_P = self.P

        # Compute identification error
        time_elapsed_sec = self.elapsed_time_sec
        curr_error = curr_acc_offset_us - prev_skew * time_elapsed_sec

        # ====================== Start of Your Code =========================
        # RLS algorithm
        # Inputs:
        #   t[k] -> time_elapsed_sec
        #   P[k-1] -> prev_P
        #   S[k-1] -> prev_skew
        #   e[k] -> curr_error
        #   lambda -> l
        #
        # Outputs:
        #   P[k] -> curr_P
        #   S[k] -> curr_skew
        #
        # TODO: Implement the RLS algorithm

        # Your code goes here. 

        # ====================== End of Your Code =========================

        # Update the state of IDS
        self.avg_offset_us = curr_avg_offset_us
        self.acc_offset_us = curr_acc_offset_us
        self.skew = curr_skew
        self.P = curr_P

        self.avg_offset_us_hist.append(curr_avg_offset_us)
        self.acc_offset_us_hist.append(curr_acc_offset_us)
        self.skew_hist.append(curr_skew)
        self.error_hist.append(curr_error)

        return curr_error

    def update_cusum(self, curr_error_sample):
        if self.k <= self.k_CUSUM_start:
            self.e_ref.append(curr_error_sample)
            return

        prev_L_upper = self.L_upper
        prev_L_lower = self.L_lower

        # Compute mu_e and sigma_e
        e_ref_arr = np.asarray(self.e_ref)
        mu_e = np.mean(e_ref_arr)
        sigma_e = np.std(e_ref_arr)

        kappa = self.kappa

        # ====================== Start of Your Code =========================
        # TODO: 1) Normalize curr_error_sample, 2) compute curr_L_upper and curr_L_lower
        # Store the normalized error in `normalized_error`

        # Your code goes here. 
        
        # ====================== End of Your Code =========================

        if (curr_L_upper > self.Gamma) | (curr_L_lower > self.Gamma):
            self.is_detected = True

        # Store valid (un-normalized) error sample
        if abs(normalized_error) < self.gamma:
            self.e_ref.append(curr_error_sample)

        # Update the state of CUSUM
        self.L_upper = curr_L_upper
        self.L_lower = curr_L_lower

        self.L_upper_hist.append(curr_L_upper)
        self.L_lower_hist.append(curr_L_lower)