from invoke import task

@task
def test(c, unit=False, integration=False):
    """ Run all unit or integration tests
    """
    if unit:
        cmd = "python3 -m unittest test/unit/test_*.py"
    elif integration:
        cmd = "python3 -m unittest test/integration/test_*.py"
    else:
        cmd = "python3 -m unittest test/*/test_*.py"
    c.run(cmd, pty=True)

@task
def fetch_lichess(c, tournament=''):
    """ Fetch all games played in a lichess tournament
    """
    if len(tournament):
        id = tournament
        c.run("curl https://lichess.org/api/tournament/%s/games > tournament.%s.pgn" % (id, id), pty=True)
