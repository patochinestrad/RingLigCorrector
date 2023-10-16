import typer
from pymol import cmd
from rich import print
from typing_extensions import Annotated

app = typer.Typer()


def format_pdb_atom_line(atom_list):
    atom_line = "{:<6s}{:>5s} {:<4s}{:>4s} {:1s}{:>4s}    {:>7s}{:>8s}{:>8s}{:>6s}{:>6s}          {:>2s}".format(
        *atom_list
    )
    return atom_line


@app.command()
def correct(
    file: Annotated[str, typer.Argument(help="Path to PDB file of the ligand")],
    compound_name: Annotated[
        str, typer.Argument(
            help="Three chracter code used to rename the ligand")
    ],
    connections: Annotated[
        bool, typer.Option(help="Output connection scheme for use with ring")
    ] = False,
    acc_dons: Annotated[
        bool,
        typer.Option(
            help="Output hydrogen bond donor and acceptor atoms for use with ring"
        ),
    ] = False,
):
    """
    Rename the atoms of a small-molecule PDB file and outputs the bond order to be used with the Ring-Pymol plugin
    """
    if len(compound_name) != 3:
        print(
            """
ERROR: COMPOUND NAME NEEDS TO BE EXACTLY 3 CHARACTERS BETWEEN LETTERS AND NUMBERS!
EXITING NOW"""
        )
        return 1
    with open(file, "r") as f, open(f"{compound_name}_correct_names.pdb", "w") as fout:
        atom_dict = {}
        keep_connections = []
        for line in f:
            if line.startswith(("ATOM", "HETATM")):
                part = line.split()
                part[2] = part[2][0] + part[1]
                atom_dict[part[1]] = part[2]
                part[3] = compound_name.upper()
                fout.write(format_pdb_atom_line(part) + "\n")
            elif line.startswith("CONECT"):
                fout.write(line)
                parts = line.split()[1:]
                node = parts[0]
                all_connections = parts[1:]
                local_connections = list(
                    set([con for con in all_connections if int(con) > int(node)])
                )
                local_connections.insert(0, node)
                if len(local_connections) > 1:
                    keep_connections.append(local_connections)

        if connections:
            with open(f"{compound_name}_connections_for_ring.txt", "w") as ringout:
                ringout.write(compound_name + "\n")
                for connects in keep_connections:
                    correct_naming = [atom_dict[value] for value in connects]
                    ringout.write(" ".join(correct_naming) + "\n")

    if acc_dons:
        cmd.load(f"{compound_name}_correct_names.pdb")
        atoms = {"acceptors": [], "donors": []}
        cmd.select("acc.")
        cmd.iterate("(sele)", "acceptors.append(name)", space=atoms)
        cmd.select("don.")
        cmd.iterate("(sele)", "donors.append(name)", space=atoms)
        with open(f"{compound_name}_acc_and_dons.txt", "w") as f:
            f.write(f"# {compound_name}\n")
            f.write("A:" + " ".join(atoms["acceptors"]) + "\n")
            f.write("D:" + " ".join(atoms["donors"]))


if __name__ == "__main__":
    app()
