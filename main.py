import teachers.omniscient_teacher as omni
import numpy as np
import matplotlib.pyplot as plt
import torch as th
import sys
import data.dataset_loader as dataset_loader
from sklearn.decomposition import PCA

if __name__ == "__main__":
    # X1 = np.random.multivariate_normal([0, 0], np.identity(2), 1000)
    # y1 = np.ones((1000,))

    # X2 = np.random.multivariate_normal([1.4, 1.4], np.identity(2), 1000)
    # y2 = np.zeros((1000,))

    # X = np.concatenate((X1, X2), axis=0)
    # y = np.concatenate((y1, y2), axis=0)

    # indices = np.indices((2000,))
    # np.random.shuffle(indices)

    # X = X[indices]
    # y = y[indices]

    mnistfile="./data/mnist.pkl.gz"
    train_set, valid_set, test_set = dataset_loader.load_mnist(mnistfile)

    X_train = np.asarray(train_set[0])
    Y_train = np.asarray(train_set[1])

    # Traitement PCA pour obtenir 24 composantes
    # pca = PCA(n_components = 24)
    # pca.fit(X_train)
    # X_train = pca.transform(X_train)

    print(X_train.shape)
    print(Y_train.shape)

    X = X_train[Y_train <= 1]
    y = Y_train[Y_train <= 1]

    X = X[:2000]
    y = y[:2000]

    randomize = np.arange(X.shape[0])
    np.random.shuffle(randomize)
    X = X[randomize]
    y = y[randomize]

    print(X.shape)
    print(y.shape)


    # On entraine le teacher
    """
    sl = nn.SingleLayer(2, 2)
    epoch = 10
    for e in range(epoch):
        for data, label in zip(X, y):
            gbw = sl.compute_gradient(data.reshape(1, -1), label)
            sl.step(gbw)
        res = np.argmax(sl.forward(X), axis=1)
        nb_correct = (res == y).sum()
        print(nb_correct, "/", X.shape[0])

    # test student
    omni_sl = omni.OmniscientSingleLayer(2, 2)
    print(omni_sl.example_difficulty(X[None, 0], y[None, 0]))
    print(omni_sl.example_use_fullness(sl.weights, X[None, 0], y[None, 0]))
    """
    """
    for e in range(2):
        for data, label in zip(X, y):
            gbw = omni_sl.compute_gradient(data.reshape(1, -1), label)
            omni_sl.step(gbw)
    print(omni_sl.example_difficulty(X[None, 0], y[None, 0]))
    """
    teacher = omni.OmniscientLinearClassifier(784)
    example = omni.OmniscientLinearClassifier(784)
    student = omni.OmniscientLinearClassifier(784)

    X = th.Tensor(X)
    y = th.Tensor(y).view(-1)

    print(X.size())
    print(y.size())

    print(y)

    for e in range(30):
        for i in range(200):
            i_min = i * 10
            i_max = (i + 1) * 10
            teacher.update(X[i_min:i_max], y[i_min:i_max])
        test = teacher(X)
        tmp = th.where(test > 0.5, th.ones(1), th.zeros(1))
        nb_correct = th.where(tmp.view(-1) == y, th.ones(1), th.zeros(1)).sum().item()
        print(nb_correct, "/", X.size(0))

    T = 200

    res_example = []

    for t in range(T):
        i = th.randint(0, X.size(0), size=(1,)).item()
        data = X[i]
        label = y[i]
        example.update(data, label)
        test = example(X)
        tmp = th.where(test > 0.5, th.ones(1), th.zeros(1))
        nb_correct = th.where(tmp.view(-1) == y, th.ones(1), th.zeros(1)).sum().item()
        res_example.append(nb_correct / X.size(0))

    print("Base line trained\n")

    res_student = []

    for t in range(T):
        scores = []
        for data, label in zip(X, y):
            eta = student.optim.param_groups[0]["lr"]
            s = (eta ** 2) * student.example_difficulty(data, label)
            s -= eta * 2 * student.example_usefulness(teacher.lin.weight, data, label)
            scores.append(s)

        i = np.argmin(scores)
        x_t = X[i]
        y_t = y[i]
        student.update(x_t, y_t)

        test = student(X)
        tmp = th.where(test > 0.5, th.ones(1), th.zeros(1))
        nb_correct = th.where(tmp.view(-1) == y, th.ones(1), th.zeros(1)).sum().item()
        res_student.append(nb_correct / X.size(0))

        sys.stdout.write("\r" + str(t) + "/" + str(T) + ", idx=" + str(i) + " " * 100)
        sys.stdout.flush()

    plt.plot(res_example, c='b')
    plt.plot(res_student, c='r')
    plt.show()








