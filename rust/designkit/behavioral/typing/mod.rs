use pyo3::prelude::*;

pub mod core;

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    core::register(m)?;

    Ok(())
}