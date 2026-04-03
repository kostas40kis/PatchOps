from patchops.failure_categories import (
    AMBIGUOUS_OR_SUSPICIOUS_RUN,
    PATCH_AUTHORING_FAILURE,
    TARGET_PROJECT_FAILURE,
    WRAPPER_FAILURE,
    FailureCategoryModel,
    is_known_failure_category,
    known_failure_categories,
    normalize_failure_category,
    unique_failure_categories,
)


def test_failure_category_model_exposes_maintained_vocabulary() -> None:
    assert known_failure_categories() == (
        TARGET_PROJECT_FAILURE,
        WRAPPER_FAILURE,
        PATCH_AUTHORING_FAILURE,
        AMBIGUOUS_OR_SUSPICIOUS_RUN,
    )


def test_failure_category_model_dataclass_matches_tuple_order() -> None:
    model = FailureCategoryModel()
    assert model.as_tuple() == known_failure_categories()


def test_failure_category_normalization_falls_back_to_ambiguous() -> None:
    assert normalize_failure_category(None) == AMBIGUOUS_OR_SUSPICIOUS_RUN
    assert normalize_failure_category("not_a_real_class") == AMBIGUOUS_OR_SUSPICIOUS_RUN
    assert normalize_failure_category(" wrapper_failure ") == WRAPPER_FAILURE


def test_failure_category_recognition_and_uniqueness() -> None:
    assert is_known_failure_category(TARGET_PROJECT_FAILURE) is True
    assert is_known_failure_category("made_up") is False
    assert unique_failure_categories(
        [
            TARGET_PROJECT_FAILURE,
            " wrapper_failure ",
            None,
            "made_up",
            TARGET_PROJECT_FAILURE,
        ]
    ) == (
        TARGET_PROJECT_FAILURE,
        WRAPPER_FAILURE,
        AMBIGUOUS_OR_SUSPICIOUS_RUN,
    )
