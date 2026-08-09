use pyo3::prelude::*;

pub mod typing;

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let typing = PyModule::new(m.py(), "typing")?;

    typing::register(&typing)?;

    m.add_submodule(&typing)?;

    Ok(())
}
