#!/usr/bin/env bash
python_versions=("${@}")

for version in ${python_versions[*]};
do
  pyenv local "$version"
  python_executable_path=$(pyenv which python)
  ln -s "$python_executable_path" "/usr/bin/python$version"
done

last_python_bin_path=$(dirname "$(pyenv which python)")
ln -s "$last_python_bin_path" "./python_bin"
