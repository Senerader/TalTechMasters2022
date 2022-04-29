import matplotlib.pyplot as plt
import numpy as np
i = 0
while i < 9:
    with open(f'tmp_data/observations_{i}.csv', 'r') as t1, open(f'data_no_disturbances_rl/observations_{i}.csv', 'r') as t2:
        fileone = t1.readlines()
        for idx, obs in enumerate(fileone):
            obs = list(map(float, obs.split(',')))
            fileone[idx] = obs #type: ignore
        filetwo = t2.readlines()
        for idx, obs in enumerate(filetwo):
            obs = list(map(float, obs.split(',')))
            filetwo[idx] = obs #type: ignore
    with open(f'data_no_disturbances_rl/actions_{i}.csv', 'r') as t2:
        actions = t2.readlines()
        actions = list(map(float, actions))
    xrange = list(range(1, 501))
    fileone = np.asarray(fileone)
    filetwo = np.asarray(filetwo)
    # Actions
    plt.subplot(6, 1, 1)
    plt.plot(xrange[:len(actions)], actions, color='r', label='actions')
    plt.xlabel("Timestep")
    plt.ylabel("Action")
    plt.title("Actions")
    plt.legend()
    # Cart pos
    plt.subplot(6, 1, 2)
    plt.plot(xrange[:len(fileone)], fileone[:, 0], color='r', label='virtual')
    plt.plot(xrange[:len(filetwo)], filetwo[:, 0], color='g', label='physical')
    plt.xlabel("Timestep")
    plt.ylabel("Pose [m]")
    plt.title("Cart Pos")
    plt.legend()
    # Cart vel
    plt.subplot(6, 1, 3)
    plt.plot(xrange[:len(fileone)], fileone[:, 1], color='r', label='virtual')
    plt.plot(xrange[:len(filetwo)], filetwo[:, 1], color='g', label='physical')
    plt.xlabel("Timestep")
    plt.ylabel("Vel [m/s]")
    plt.title("Cart Vel")
    plt.legend()
    # Pole sin
    plt.subplot(6, 1, 4)
    plt.plot(xrange[:len(fileone)], fileone[:, 2], color='r', label='virtual')
    plt.plot(xrange[:len(filetwo)], filetwo[:, 2], color='g', label='physical')
    plt.xlabel("Timestep")
    plt.ylabel("Sin")
    plt.title("Pole sine")
    plt.legend()
    # Pole cos
    plt.subplot(6, 1, 5)
    plt.plot(xrange[:len(fileone)], fileone[:, 3], color='r', label='virtual')
    plt.plot(xrange[:len(filetwo)], filetwo[:, 3], color='g', label='physical')
    plt.xlabel("Timestep")
    plt.ylabel("Cos")
    plt.title("Pole cosine")
    plt.legend()
    # Pole vel
    plt.subplot(6, 1, 6)
    plt.plot(xrange[:len(fileone)], fileone[:, 4], color='r', label='virtual')
    plt.plot(xrange[:len(filetwo)], filetwo[:, 4], color='g', label='physical')
    plt.xlabel("Timestep")
    plt.ylabel("Pole vel [rad/s]")
    plt.title("Pole velocity")
    plt.legend()
    plt.show(block=True)
    i += 1