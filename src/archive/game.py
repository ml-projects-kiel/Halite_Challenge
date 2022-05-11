from kaggle_environments import evaluate, make

env = make("halite", debug=True)
env.run(["random", "random", "random", "random"])
env.render(mode="ipython", width=800, height=600)
