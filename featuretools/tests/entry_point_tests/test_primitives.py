import pytest
import featuretools as ft
from featuretools.primitives import MultiplyNumericScalar, Year

from featuretools.tests.entry_point_tests.utils import (
    _import_featuretools,
    _install_featuretools_primitives,
    _python,
    _uninstall_featuretools_primitives,
)


def test_entry_point():
    _install_featuretools_primitives()
    featuretools_log = _import_featuretools("debug").stdout.decode()
    new_primitive = _python("-c", "from featuretools.primitives import NewPrimitive")
    _uninstall_featuretools_primitives()
    assert new_primitive.returncode == 0

    invalid_primitive = 'Featuretools failed to load "invalid" primitives from "featuretools_primitives.invalid_primitive". '
    invalid_primitive += "For a full stack trace, set logging to debug."
    assert invalid_primitive in featuretools_log

    existing_primitive = 'While loading primitives via "existing" entry point, '
    existing_primitive += 'ignored primitive "Sum" from "featuretools_primitives.existing_primitive" because a primitive '
    existing_primitive += 'with that name already exists in "featuretools.primitives.standard.aggregation.sum_primitive"'
    assert existing_primitive in featuretools_log


primitive_test_data = [
    (MultiplyNumericScalar(2), [1, 2.5, -3], float),
    (Year(), ["2020-01-01", "2019-12-31"], int)
]

@pytest.mark.parametrize("primitive, values, expected_dtype", primitive_test_data)
def test_primitive_input_types(primitive, values, expected_dtype):
    es = ft.demo.load_retail(nrows=5)
    fm, features = ft.dfs(
        entityset=es,
        target_dataframe_name="orders",
        trans_primitives=[primitive],
        max_depth=1,
    )
    col = features[-1].name
    dtype = fm[col].dtype
    assert expected_dtype in str(dtype), f"{primitive} returned dtype {dtype}"
