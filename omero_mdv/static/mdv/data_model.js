// datasources is the data model - updated via AJAX when user updates form
class DataModel extends EventTarget {

    // each table item is {id: {columns:[], etc} }
    omero_tables = []
    // map-anns, datasets, tags etc have columns in mdv format
    // but the data is not ordered
    unordered_data = []

    // Expect a single Table, which is "ordered"
    // tableData has mdv "columns"
    addTable(tableId, tableData) {
      console.log("test addTable...")
      tableData.id = tableId
      this.omero_tables.push(tableData);
      this.dispatchEvent(new CustomEvent("dataAdded", {}));
    }

    removeTable(tableId) {
      this.omero_tables = this.omero_tables.filter(table => table.id != tableId);
      this.dispatchEvent(new CustomEvent("dataAdded", {}));
    }

    // Handles "unordered" data: Map-Anns and Datasets
    // tableData has mdv "columns"
    addMapAnns(sourceId, tableData) {
      console.log("ADD MAP-ANNS! ", tableData)
      tableData.id = sourceId
      this.unordered_data.push(tableData);
      this.dispatchEvent(new CustomEvent("dataAdded", {}));
    }

    removeMapAnns(sourceId) {
      this.unordered_data = this.unordered_data.filter(table => table.id != sourceId);
      this.dispatchEvent(new CustomEvent("dataAdded", {}));
    }

    getColumns() {
      let cols = [this.omero_tables, this.unordered_data].flatMap(dsrc => dsrc.flatMap(ds => ds.columns));
      return cols;
    }

    getNumberColumns() {
        return this.getColumns().filter(col => col.datatype == "double" || col.datatype == "integer")
    }

    getStringColumns() {
        return this.getColumns().filter(col => col.datatype == "text" || col.datatype == "multitext")
    }

    getRowData() {
      const cols = this.getColumns();
      if (cols.length == 0) {
        return [];
      }

      function getVal(column, rowIndex) {
        if (column.datatype == "double" || column.datatype == "integer") {
          return column.data[rowIndex];
        }
        if (column.datatype == "text") {
          let idx = column.data[rowIndex];
          return idx == 65535 ? "" : column.values[idx];
        }
        if (column.datatype == "multitext") {
          let offset = rowIndex * column.stringLength;
          let indicies = column.data.slice(offset, offset + column.stringLength);
          return indicies.map(idx => idx == 65535 ? "" : column.values[idx]).filter(Boolean).join(", ");
        }
        return "";
      }

      let primaryKeys = cols[0].data;

      let rowsData = primaryKeys.map((pk, index) => {
        // TODO - sort unordered data by primary key
        let row = cols.map(col => getVal(col, index));
        return row;
      });
      return rowsData;
    }
  }
