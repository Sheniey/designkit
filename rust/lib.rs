use pyo3::prelude::*;
use pyo3_stub_gen::define_stub_info_gatherer;
mod designkit;

#[pymodule]
fn _designkit(m: &Bound<'_, PyModule>) -> PyResult<()> {
    designkit::register(m)?;
    Ok(())
}

define_stub_info_gatherer!(stub_info);