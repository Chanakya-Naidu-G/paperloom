from app.ingestion.chunking.section_detector import is_heading


def test_detects_known_research_heading():
    assert is_heading("ABSTRACT") == "Abstract"
    assert is_heading("1. INTRODUCTION") == "Introduction"
    assert is_heading("2. RELATED WORK") == "Related Work"


def test_detects_title_case_heading():
    assert is_heading("Learning Methods") == "Learning Methods"
    assert is_heading("Biological Neuron") == "Biological Neuron"
    assert is_heading("Hebb Network") == "Hebb Network"


def test_detects_question_heading():
    assert is_heading("What is a neuron?") == "What Is A Neuron?"
    assert (
        is_heading("What is a (an Artificial) Neural Network?")
        == "What Is A (An Artificial) Neural Network?"
    )


def test_does_not_detect_bullet_as_heading():
    assert (
        is_heading(
            "• Neural network was inspired by the design and functioning of human brain."
        )
        is None
    )


def test_does_not_detect_normal_sentence_as_heading():
    assert (
        is_heading(
            "A neuron is the basic processing unit in a neural network."
        )
        is None
    )


def test_does_not_detect_long_text_as_heading():
    assert (
        is_heading(
            "The neural network receives inputs and processes them using interconnected neurons."
        )
        is None
    )


def test_does_not_detect_definition_label_as_heading():
    assert is_heading("Definition:") is None


def test_does_not_detect_single_word_content_as_heading():
    assert is_heading("However") is None