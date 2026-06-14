import ask


def test_run_cli_processes_questions_until_stop_command(monkeypatch, capsys):
    questions = iter(["Какой грунт лучше?", "exit"])
    calls = []

    def fake_ask(question):
        calls.append(question)

    monkeypatch.setattr(ask, "ask", fake_ask)
    ask.run_cli(input_func=lambda prompt: next(questions))

    captured = capsys.readouterr()
    assert "Задавайте вопросы по помашнему огороду" in captured.out
    assert calls == ["Какой грунт лучше?"]


def test_run_cli_stops_immediately_for_stop_words(monkeypatch, capsys):
    questions = iter(["stop"])
    calls = []

    def fake_ask(question):
        calls.append(question)

    monkeypatch.setattr(ask, "ask", fake_ask)
    ask.run_cli(input_func=lambda prompt: next(questions))

    captured = capsys.readouterr()
    assert calls == []
    assert "Задавайте вопросы по помашнему огороду" in captured.out
