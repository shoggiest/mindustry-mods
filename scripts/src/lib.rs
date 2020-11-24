use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

/// This module is implemented in Rust.
#[pymodule]
fn scripts(_py: Python, module: &PyModule) -> PyResult<()> {
    #[pyfn(module, "dump")]
    fn dump(_py: Python, mods: Vec<Mod>) -> PyResult<String> {
        Ok(serde_json::to_string(&mods).unwrap())
    }

    module.add_class::<Mod>()?;
    Ok(())
}

#[pyclass]
#[derive(Deserialize, Serialize, FromPyObject)]
pub struct Mod {
    /// mod name
    pub name: String,
    /// mod name with markup
    pub name_markup: String,
    /// link to repository
    pub link: String,
    pub repo: String,
    /// short description
    pub desc: String,
    /// short description with markup
    pub desc_markup: Option<String>,
    pub icon: Option<String>,
    /// repository stars
    pub stars: u32,
    /// author name
    pub author: String,
    /// author name with markup
    pub author_markup: Option<String>,
    /// last commit ISO formatted datetime
    pub date: String,
    /// last commit UTC timestamp epoch in seconds
    pub date_tt: f64,
    pub readme: String,
    pub version: Option<String>,
    pub assets: Vec<String>,
    pub contents: Vec<String>,
    /// markup encoded name
    #[serde(rename = "camelCase")]
    pub display_name: Option<String>,
}

#[pymethods]
impl Mod {
    #[new]
    pub fn new(
        name: String,
        name_markup: String,
        link: String,
        repo: String,
        desc: String,
        desc_markup: Option<String>,
        icon: Option<String>,
        stars: u32,
        author: String,
        author_markup: Option<String>,
        date: String,
        date_tt: f64,
        readme: String,
        version: Option<String>,
        assets: Vec<String>,
        contents: Vec<String>,
        display_name: Option<String>,
    ) -> PyResult<Self> {
        Ok(Self {
            name,
            name_markup,
            link,
            repo,
            desc,
            desc_markup,
            icon,
            stars,
            author,
            author_markup,
            date,
            date_tt,
            readme,
            version,
            assets,
            contents,
            display_name,
        })
    }

    pub fn date_tt(&self) -> PyResult<f64> {
        Ok(self.date_tt)
    }
}